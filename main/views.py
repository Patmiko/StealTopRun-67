from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q, Prefetch
from django.views import View
from .models import User, Game, Speedrun, SpeedrunType, VerificationStatus
from .forms import Category, ResendVerificationForm, SpeedrunForm, GameRequestForm, SpeedrunTypeRequestForm, UserReportForm, SpeedrunReportForm, UserProfileEditForm, RegisterForm
import json
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.core import signing
from .utils import send_verification_email, send_change_email, send_security_alert_email


class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'home.html')

#USER PATHS
#===================================================================================================================

class LoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user/login.html')

    def post(self, request, *args, **kwargs):
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')

        user = None

        if '@' in username_or_email:
            # Try to find the user by email
            try:
                user_obj = User.objects.get(email=username_or_email)
                username = user_obj.username
                user = authenticate(request, username=username, password=password)
            except User.DoesNotExist:
                user = None
        else:
            # Otherwise, authenticate by username normally
            user = authenticate(request, username=username_or_email, password=password)

        if user is not None and user.status != VerificationStatus.VERIFIED:
            if user.status == VerificationStatus.UNVERIFIED:
                messages.error(request, 'Your email is not verified. Please check your inbox for the verification link.')
                return render(request, 'email_resend.html')
            else:
                messages.error(request, 'This account is inaccessible')
                return render(request, 'user/login.html')

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username/email or password.')
            return render(request, 'user/login.html')


class RegisterView(View):
    def get(self, request, *args, **kwargs):
        form = RegisterForm()
        return render(request, 'user/register.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.status = VerificationStatus.UNVERIFIED
            user.save()

            send_verification_email(request, user)

            messages.success(request, 'Verification email sent! Please check your inbox to verify your account.')
            return redirect('verification-pending')

        return render(request, 'user/register.html', {'form': form})


@method_decorator(login_required(login_url='user-login'), name='dispatch')
class LogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('user-login')

class UserProfileView(View):
    def get(self, request, username, *args, **kwargs):
        profile_user = get_object_or_404(User, username=username)

        user_runs = Speedrun.objects.filter(user=profile_user, status='ACCEPTED').select_related('speedrun_type', 'speedrun_type__game')
        
        context = {
            'profile_user': profile_user,
            'user_runs': user_runs,
        }
        return render(request, 'user/profile.html', context)

@method_decorator(login_required(login_url='user-login'), name='dispatch')
class EditUserProfileView(View):
    def get(self, request, username, *args, **kwargs):
        profile_user = get_object_or_404(User, username=username)
        
        if request.user != profile_user:
            messages.error(request, "You cannot edit someone else's profile.")
            return redirect('user-profile', username=profile_user.username)
            
        profile_form = UserProfileEditForm(instance=profile_user)
        password_form = PasswordChangeForm(user=profile_user)
        
        context = {
            'profile_user': profile_user,
            'profile_form': profile_form,
            'password_form': password_form,
            'pending_email': request.session.get('pending_email'),
        }
        return render(request, 'user/edit-profile.html', context)

    def post(self, request, username, *args, **kwargs):
        profile_user = get_object_or_404(User, username=username)
        
        if request.user != profile_user:
            messages.error(request, "You cannot edit someone else's profile.")
            return redirect('user-profile', username=profile_user.username)

        original_email = profile_user.email

        action = request.POST.get('action')
        profile_form = UserProfileEditForm(instance=profile_user)
        password_form = PasswordChangeForm(user=profile_user)

        if action == 'update_profile':
            profile_form = UserProfileEditForm(request.POST, request.FILES, instance=profile_user)
            if profile_form.is_valid():
                user_instance = profile_form.save(commit=False)
                
                new_username = profile_form.cleaned_data.get('username')
                new_email = profile_form.cleaned_data.get('email')

                has_errors = False
                if User.objects.filter(username=new_username).exclude(pk=profile_user.pk).exists():
                    profile_form.add_error('username', 'This username is already taken.')
                    has_errors = True
                    
                if User.objects.filter(email=new_email).exclude(pk=profile_user.pk).exists():
                    profile_form.add_error('email', 'This email is already taken.')
                    has_errors = True

                if not has_errors:
                    user_instance.username = new_username
                    
                    if new_email != original_email:
                        messages.info(request, 'A verification link has been sent to your new email. Please verify to complete the change.')

                        user_instance.email = original_email
                        profile_user.email = original_email
                        send_change_email(request, profile_user, new_email)
                        send_security_alert_email(request, profile_user, original_email, new_email)
                        request.session['pending_email'] = new_email
                    else:
                        user_instance.email = original_email

                    user_instance.save()
                    profile_form.save_m2m() 
                    
                    messages.success(request, 'Profile updated successfully!')
                    return redirect('user-profile', username=user_instance.username)
            else:
                messages.error(request, 'Please correct the errors in the profile form.')

        elif action == 'change_password':
            password_form = PasswordChangeForm(user=profile_user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()

                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated!')
                return redirect('user-profile', username=profile_user.username)
            else:
                messages.error(request, 'Please correct the errors in the password form.')

        context = {
            'profile_user': profile_user,
            'profile_form': profile_form,
            'password_form': password_form,
            'pending_email': request.session.get('pending_email'),
        }
        return render(request, 'user/edit-profile.html', context)

class SearchUserView(View):
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('q', '').strip()
        
        if search_query:
            users = User.objects.filter(username__icontains=search_query)
            users = users.filter(status='VERIFIED')
        else:
            users = User.objects.none()
            
        return render(request, 'user/search_users.html', {'users': users, 'search_term': search_query})
    
class DeleteUserView(View):
    @method_decorator(login_required(login_url='user-login'))
    def post(self, request, *args, **kwargs):
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('home')

# EMAIL VERIFICATION PATHS
#===================================================================================================================

class EmailVerificationView(View):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.status = VerificationStatus.VERIFIED
            user.save()
            messages.success(request, 'Your email has been verified! You can now log in.')
            return render(request, 'user/login.html')
        else:
            messages.error(request, 'Invalid or expired verification link. Please request a new one.')
            return render(request, 'email_resend.html')
        
class ResendVerificationEmailView(View):
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'email_resend.html', {'error': 'If that email is registered and unverified, a new link has been sent.'})
            
        # Check if already verified
        if user.status == VerificationStatus.VERIFIED:
            return render(request, 'email_resend.html', {'error': 'This account is already verified.'})
            
        # Check the Cooldown Cache
        cache_key = f"email_cooldown_{user.pk}"
        if cache.get(cache_key):
            return HttpResponse("Please wait 15 minutes before requesting another email.", status=429)
            
        # Send the email
        send_verification_email(request, user)
        
        # Set the cooldown timer
        cache.set(cache_key, True, timeout=900)
        
        return HttpResponse("If that email is registered and unverified, a new link has been sent.")
    
class verificationPendingView(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.status == VerificationStatus.VERIFIED:
            return redirect('home')
    
        form = ResendVerificationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.info(request, "If that email is registered and unverified, a new link has been sent.")
                return redirect('verification-pending')

            if user.status == VerificationStatus.VERIFIED:
                messages.warning(request, "This account is already verified. Please log in.")
                return redirect('user-login')

            cache_key = f"email_cooldown_{user.pk}"
            if cache.get(cache_key):
                messages.error(request, "Please wait 15 minutes before requesting another email.")
                return render(request, 'email_resend.html', {'form': form})

            # Send email and trigger cooldown
            send_verification_email(request, user)
            cache.set(cache_key, True, timeout=900)
            
            messages.success(request, "A new verification link has been sent to your email.")
            return redirect('verification-pending')
        return render(request, 'email_resend.html', {'form': form})
    def get(self, request, *args, **kwargs):
        initial_data = {}
        if request.user.is_authenticated:
            initial_data['email'] = request.user.email
        form = ResendVerificationForm(initial=initial_data)

        return render(request, 'email_resend.html', {'form': form})
    
class ChangeEmailView(View):
    def get(self, request, uidb64, token, *args, **kwargs):
        User = get_user_model()
        signed_email = request.GET.get('target')

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            new_email = signing.loads(signed_email, max_age=86400)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, 
                signing.BadSignature, signing.SignatureExpired):
            user = None
            new_email = None

        if user is not None and new_email is not None and default_token_generator.check_token(user, token):
            
            if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
                messages.error(request, "This email address is already registered to another account.")
                return redirect('user-profile', username=user.username)
            
            user.email = new_email
            user.save()
            
            if 'pending_email' in request.session:
                del request.session['pending_email']
                
            messages.success(request, "Your email has been successfully updated!")
            return redirect('user-profile', username=user.username)
        else:
            messages.error(request, "This verification link is invalid or has expired.")
            return redirect('home')
#GAME PATHS
#===================================================================================================================

class GamesView(View):
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('q', '').strip()
        
        if search_query:
            games = Game.objects.filter(name__icontains=search_query)
            grouped_games = None
        else:
            games = None
            categories = Category.objects.prefetch_related('game_set').all()
            
            grouped_games = {}
            for category in categories:
                category_games = category.game_set.all()
                
                if category_games.exists():
                    grouped_games[category.name] = category_games
            
        return render(request, 'games.html', {
            'games': games, 
            'grouped_games': grouped_games, 
            'search_term': search_query
        })

class GameDetailView(View):
    def get(self, request, game_id, *args, **kwargs):
        game = get_object_or_404(Game, pk=game_id)
        speedrun_types = game.speedrun_types.all()
        return render(request, 'game_detail.html', {'game': game, 'speedrun_types': speedrun_types})
    
#SPEEDRUN TYPES PATHS
#===================================================================================================================

class CategoryLeaderboardView(View):
    def get(self, request, game_id, type_id, *args, **kwargs):
        game = get_object_or_404(Game, pk=game_id)
        category = get_object_or_404(SpeedrunType, pk=type_id, game=game)
        
        speedruns = Speedrun.objects.filter(
            speedrun_type=category, 
            status='ACCEPTED'
        ).order_by('time')
        
        history_runs = speedruns.order_by('date')
        chart_data = []
        best_time = float('inf')
        
        def format_seconds(total_seconds):
            total_seconds = int(total_seconds)
            minutes, seconds = divmod(total_seconds, 60)
            return f"{minutes:02}:{seconds:02}"
        
        for run in history_runs:
            if float(run.time) < best_time:
                best_time = float(run.time)
                chart_data.append({
                    'date': run.date.strftime('%Y-%m-%d'),
                    'time': best_time,
                    'formatted': format_seconds(best_time) # Add this
                })

        if chart_data:
            today_str = timezone.now().strftime('%Y-%m-%d')
            chart_data.append({
                'date': today_str,
                'time': chart_data[-1]['time']
            })
        
        return render(request, 'category_leaderboard.html', {
            'game': game,
            'category': category,
            'speedruns': speedruns,
            'chart_data': json.dumps(chart_data) # Pass as JSON string
        })

#SPEEDRUN PATHS
#===================================================================================================================

class SpeedrunDetailView(View):
    def get(self, request, game_id, type_id, speedrun_id, *args, **kwargs):
        game = get_object_or_404(Game, pk=game_id)
        category = get_object_or_404(SpeedrunType, pk=type_id, game=game)
        speedrun = get_object_or_404(Speedrun, pk=speedrun_id, speedrun_type=category)
        
        rank = Speedrun.objects.filter(
            speedrun_type=category, 
            status='ACCEPTED', 
            time__lt=speedrun.time
        ).count() + 1
        
        return render(request, 'speedrun_detail.html', {
            'game': game,
            'category': category,
            'speedrun': speedrun,
            'rank': rank
        })

@method_decorator(login_required(login_url='user-login'), name='dispatch')
class SpeedrunUploadView(View):
    def get(self, request, game_id, type_id, *args, **kwargs):
        game = get_object_or_404(Game, pk=game_id)
        speedrun_type = get_object_or_404(SpeedrunType, pk=type_id, game=game)
        
        form = SpeedrunForm(initial={'speedrun_type':speedrun_type})
        return render(request, 'submit_speedrun.html', {
            'form': form,
            'game': game,
            'speedrun_type': speedrun_type
        })

    def post(self, request, game_id, type_id, *args, **kwargs):
        game = get_object_or_404(Game, pk=game_id)
        speedrun_type = get_object_or_404(SpeedrunType, pk=type_id, game=game)
        
        form = SpeedrunForm(request.POST)
        
        if form.is_valid():
            speedrun = form.save(commit=False)
            
            speedrun.user = request.user
            speedrun.speedrun_type = speedrun_type 
            speedrun.status = 'PENDING'
            
            speedrun.save()
            messages.success(request, f'Your {speedrun_type.name} speedrun for {game.name} has been submitted for review!')
            
            return redirect('category-leaderboard', game_id=game.id, type_id=type_id)
        else:
            return render(request, 'submit_speedrun.html', {
                'form': form,
                'game': game,
                'speedrun_type': speedrun_type
            })
        
class SpeedrunDeleteView(View):
    @method_decorator(login_required(login_url='user-login'))
    def post(self, request, game_id, type_id, speedrun_id, *args, **kwargs):
        speedrun = get_object_or_404(Speedrun, pk=speedrun_id, speedrun_type__id=type_id)
        
        # Security check: ensure only the owner can delete
        if request.user == speedrun.user:
            speedrun.delete()
            messages.success(request, 'Speedrun deleted successfully.')
        else:
            messages.error(request, 'You do not have permission to delete this run.')
            
        return redirect('category-leaderboard', game_id=game_id, type_id=type_id)

class DiscoverView(View):
    def get(self, request, *args, **kwargs):
        one_week_ago = timezone.now().date() - timedelta(days=7)
        
        # Filter runs from the last 7 days
        recent_accepted_runs = Q(speedruns__status='ACCEPTED', speedruns__date__gte=one_week_ago)
        
        # Get the valid runs
        valid_runs = Prefetch(
            'speedruns',
            queryset=Speedrun.objects.filter(status='ACCEPTED').select_related('user').order_by('time'),
            to_attr='top_runs'
        )

        # Get top 5 categories by runs
        top_categories = SpeedrunType.objects.select_related('game').annotate(
            recent_run_count=Count('speedruns', filter=recent_accepted_runs)
        ).filter(
            recent_run_count__gt=0 
        ).order_by('-recent_run_count').prefetch_related(valid_runs)[:5]

        return render(request, 'discover.html', {'top_categories': top_categories})

#REQUESTS PATHS
#===================================================================================================================
@method_decorator(login_required(login_url='user-login'), name='dispatch')
class RequestSubmissionView(View):
    def get(self, request, *args, **kwargs):
        # Instantiate both forms empty for the page load
        context = {
            'game_form': GameRequestForm(),
            'type_form': SpeedrunTypeRequestForm(),
        }
        return render(request, 'submit_request.html', context)

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        
        game_form = GameRequestForm()
        type_form = SpeedrunTypeRequestForm()

        if action == 'game_request':
            game_form = GameRequestForm(request.POST)
            if game_form.is_valid():
                game_req = game_form.save(commit=False)
                game_req.user = request.user
                game_req.save()
                messages.success(request, 'Your Game Request has been submitted for review!')
                return redirect('request-submit')

        elif action == 'type_request':
            type_form = SpeedrunTypeRequestForm(request.POST)
            if type_form.is_valid():
                type_req = type_form.save(commit=False)
                type_req.user = request.user
                type_req.save()
                messages.success(request, 'Your Category Request has been submitted for review!')
                return redirect('request-submit')

        return render(request, 'submit_request.html', {
            'game_form': game_form,
            'type_form': type_form,
        })

#REPORTS PATHS
#===================================================================================================================

@method_decorator(login_required(login_url='user-login'), name='dispatch')
class ReportUserView(View):
    def get(self, request, username, *args, **kwargs):
        target_user = get_object_or_404(User, username=username)
        
        # cant report yourself
        if target_user == request.user:
            messages.error(request, "You cannot report yourself.")
            return redirect('user-profile', username=username)
            
        form = UserReportForm()
        return render(request, 'report_form.html', {
            'form': form, 
            'target_name': target_user.username,
            'report_type': 'User'
        })

    def post(self, request, username, *args, **kwargs):
        target_user = get_object_or_404(User, username=username)
        form = UserReportForm(request.POST)
        
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.target = target_user
            report.status = 'PENDING'
            report.save()
            
            messages.success(request, f'You have successfully reported {target_user.username}. Our moderators will look into it.')
            return redirect('user-profile', username=username)
            
        return render(request, 'report_form.html', {
            'form': form, 
            'target_name': target_user.username,
            'report_type': 'User'
        })

@method_decorator(login_required(login_url='user-login'), name='dispatch')
class ReportSpeedrunView(View):
    def get(self, request, speedrun_id, *args, **kwargs):
        target_run = get_object_or_404(Speedrun, pk=speedrun_id)
        
        form = SpeedrunReportForm()
        return render(request, 'report_form.html', {
            'form': form, 
            'target_name': f"{target_run.speedrun_type.game.name} - {target_run.formatted_time}s by {target_run.user.username}",
            'report_type': 'Speedrun'
        })

    def post(self, request, speedrun_id, *args, **kwargs):
        target_run = get_object_or_404(Speedrun, pk=speedrun_id)
        form = SpeedrunReportForm(request.POST)
        
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.target = target_run
            report.status = 'PENDING'
            report.save()
            
            messages.success(request, 'Speedrun reported successfully. Moderators will review it shortly.')
            return redirect('speedrun-view', game_id=target_run.speedrun_type.game.id, type_id=target_run.speedrun_type.id, speedrun_id=target_run.id)
            
        return render(request, 'report_form.html', {
            'form': form, 
            'target_name': f"{target_run.speedrun_type.game.name} - {target_run.time}s",
            'report_type': 'Speedrun'
        })
    
# ERROR HANDLING PATHS
#===================================================================================================================
class PageNotFoundView(View):
    def get(self, request, *args, **kwargs):
        return render(request, '404.html', status=404)
    

    
    