from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from .models import User, Game, Speedrun, SpeedrunType
from .forms import SpeedrunForm

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

class SpeedrunDetailView(View):
    def get(self, request, game_id, type_id, speedrun_id, *args, **kwargs):
        # Verify the exact route context exists
        game = get_object_or_404(Game, pk=game_id)
        category = get_object_or_404(SpeedrunType, pk=type_id, game=game)
        
        # grab the specific speedrun
        speedrun = get_object_or_404(Speedrun, pk=speedrun_id, category=category)
        
        # Render the page
        return render(request, 'speedrun_detail.html', {
            'game': game,
            'category': category,
            'speedrun': speedrun
        })

@method_decorator(login_required(login_url='user-login'), name='dispatch')
class SpeedrunUploadView(View):
    def get(self, request, game_id, type_id, *args, **kwargs):
        # Optional: Grab the game and category just to display their names on the submission page
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
            speedrun.category = category 
            speedrun.status = 'PENDING'
            
            speedrun.save()
            messages.success(request, f'Your {category.name} speedrun for {game.name} has been submitted for review!')
            
            return redirect('category-leaderboard', game_id=game.id, category_id=category.id)
        else:
            return render(request, 'submit_speedrun.html', {
                'form': form,
                'game': game,
                'category': category
            })

#SPEEDRUN PATHS
#===================================================================================================================

@method_decorator(login_required(login_url='user-login'), name='dispatch')
class SpeedrunUploadView(View):
    def get(self, request, *args, **kwargs):
        form = SpeedrunForm()
        return render(request, 'submit_speedrun.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = SpeedrunForm(request.POST)
        if form.is_valid():
            speedrun = form.save(commit=False)
            speedrun.user = request.user
            speedrun.status = 'PENDING'
            speedrun.save()
            messages.success(request, 'Your speedrun has been submitted and is pending review!')
            return redirect('home')
        else:
            return render(request, 'submit_speedrun.html', {'form': form})
        
#REQUESTS PATHS
#===================================================================================================================


#REPORTS PATHS
#===================================================================================================================
