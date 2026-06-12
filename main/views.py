from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from .models import User, Game
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
            return redirect('game-base')
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
    
#GAME PATHS
#===================================================================================================================

class GameListView(View):
    def get(self, request, *args, **kwargs):
        games = Game.objects.all()
        return render(request, 'game_list.html', {'games': games})

class GameSearchView(View):
    def get(self, request, name, *args, **kwargs):
        games = Game.objects.filter(name__icontains=name)
        return render(request, 'game_list.html', {'games': games, 'search_term': name})
    
    
#SPEEDRUN TYPES PATHS
#===================================================================================================================

class SpeedrunTypeListView(View):
    def get(self, request, game_id):
        game = get_object_or_404(Game, pk=game_id)
        types = game.speedrun_types.all()
        return render(request, 'speedrun_type_list.html', {'game': game, 'types': types})

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
