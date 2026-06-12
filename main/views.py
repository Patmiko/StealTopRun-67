from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from .models import User, Game, Speedrun, SpeedrunType
from .forms import SpeedrunForm, GameRequestForm, SpeedrunTypeRequestForm, UserReportForm, SpeedrunReportForm


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

        # Create the User
        user = User.objects.create_user(username=username, email=email, password=password)
        
        messages.success(request, 'Account created successfully! Please log in.')
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


#GAME PATHS
#===================================================================================================================


class GamesView(View):
    def get(self, request, *args, **kwargs):
        # Captures from the search term from the URL (e.g., /games/?q=mario)
        search_query = request.GET.get('q', '').strip()
        
        if search_query:
            games = Game.objects.filter(name__icontains=search_query)
        else:
            games = Game.objects.all()
            
        return render(request, 'games.html', {'games': games, 'search_term': search_query})


class GameDetailView(View):
    def get(self, request, game_id, *args, **kwargs):
        game = get_object_or_404(Game, pk=game_id)
        categories = game.speedrun_types.all()
        return render(request, 'game_detail.html', {'game': game, 'categories': categories})
    
    
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
        
        return render(request, 'category_leaderboard.html', {
            'game': game,
            'category': category,
            'speedruns': speedruns
        })

#SPEEDRUN PATHS
#===================================================================================================================

class SpeedrunDetailView(View):
    def get(self, request, game_id, type_id, speedrun_id, *args, **kwargs):
        # Verify the exact route context exists
        game = get_object_or_404(Game, pk=game_id)
        category = get_object_or_404(SpeedrunType, pk=type_id, game=game)
        
        # grab the specific speedrun
        speedrun = get_object_or_404(Speedrun, pk=speedrun_id, speedrun_type=type_id)
        
        # Render the page
        return render(request, 'speedrun_detail.html', {
            'game': game,
            'category': category,
            'speedrun': speedrun
        })

@method_decorator(login_required(login_url='user-login'), name='dispatch')
class SpeedrunUploadView(View):
    def get(self, request, game_id, type_id, *args, **kwargs):
        game = get_object_or_404(Game, pk=game_id)
        category = get_object_or_404(SpeedrunType, pk=type_id, game=game)
        
        form = SpeedrunForm()
        return render(request, 'submit_speedrun.html', {
            'form': form,
            'game': game,
            'category': category
        })

    def post(self, request, game_id, type_id, *args, **kwargs):
        game = get_object_or_404(Game, pk=game_id)
        category = get_object_or_404(SpeedrunType, pk=type_id, game=game)
        
        form = SpeedrunForm(request.POST)
        
        if form.is_valid():
            speedrun = form.save(commit=False)
            
            speedrun.user = request.user
            speedrun.speedrun_type = category 
            speedrun.status = 'PENDING'
            
            speedrun.save()
            messages.success(request, f'Your {category.name} speedrun for {game.name} has been submitted for review!')
            
            return redirect('category-leaderboard', game_id=game.id, type_id=type_id)
        else:
            return render(request, 'submit_speedrun.html', {
                'form': form,
                'game': game,
                'category': category
            })

        
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
            'target_name': f"{target_run.speedrun_type.game.name} - {target_run.time}s by {target_run.user.username}",
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