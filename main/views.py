import token
from urllib import request

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q, Prefetch
from django.views import View
from .models import User, Game, Speedrun, SpeedrunType, VerificationStatus
from .forms import Category, ResendVerificationForm, SpeedrunForm, GameRequestForm, SpeedrunTypeRequestForm, UserReportForm, SpeedrunReportForm, UserProfileEditForm
import json
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from .utils import send_verification_email


class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'home.html')

#USER PATHS
#===================================================================================================================

class LoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user/login.html')

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.status != VerificationStatus.VERIFIED:
            messages.error(request, 'Your email is not verified. Please check your inbox for the verification link.')
            return render(request, 'email_resend.html')
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'user/login.html')


class RegisterView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user/register.html')

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        email = request.POST.get('email', '')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'user/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
            return render(request, 'user/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered.')
            return render(request, 'user/register.html')

        # Create the User
        user = User.objects.create_user(username=username, email=email, password=password)
        user.status = VerificationStatus.UNVERIFIED
        user.save()
        # Send the verification email
        send_verification_email(request, user)
        
        messages.success(request, 'Verification email sent! Please check your inbox to verify your account before logging in.')
        return redirect('user-login')

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
        }
        return render(request, 'user/edit-profile.html', context)

    def post(self, request, username, *args, **kwargs):
        profile_user = get_object_or_404(User, username=username)
        
        if request.user != profile_user:
            messages.error(request, "You cannot edit someone else's profile.")
            return redirect('user-profile', username=profile_user.username)

        action = request.POST.get('action')
        profile_form = UserProfileEditForm(instance=profile_user)
        password_form = PasswordChangeForm(user=profile_user)

        if action == 'update_profile':
            profile_form = UserProfileEditForm(request.POST, request.FILES, instance=profile_user)
            if profile_form.is_valid():
                user = profile_form.save()
                messages.success(request, 'Profile updated successfully!')

                return redirect('user-profile', username=user.username)
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


# EMAIL VERIFICATION PATHS
#===================================================================================================================
class EmailVerificationView(View):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
        # Decrypt the User ID
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # Check if the user exists and the token is valid/unexpired
        if user is not None and default_token_generator.check_token(user, token):
            # Update custom VerificationStatus
            user.status = VerificationStatus.VERIFIED
            user.save()
            return HttpResponse("Email verified successfully! You can now log in.")
        else:
            return HttpResponse("This verification link is invalid or has expired.", status=400)
        
class ResendVerificationEmailView(View):
    @method_decorator(login_required(login_url='user-login'))
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return HttpResponse("If that email is registered and unverified, a new link has been sent.")
            
        # Check if already verified
        if user.status == VerificationStatus.VERIFIED:
            return HttpResponse("This account is already verified.", status=400)
            
        # Check the Cooldown Cache
        cache_key = f"email_cooldown_{user.pk}"
        if cache.get(cache_key):
            return HttpResponse("Please wait 2 minutes before requesting another email.", status=429)
            
        # Send the email
        send_verification_email(request, user)
        
        # Set the cooldown timer
        cache.set(cache_key, True, timeout=120)
        
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
    

    
    