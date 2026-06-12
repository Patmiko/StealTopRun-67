from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Profile,Post,LikePost,FollowersCount
from django.contrib.auth.decorators import login_required
from itertools import chain
import random
from django.views import View


class LoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user/login.html')

    def post(self, request, *args, **kwargs):
        
        return redirect('game-base')

class RegisterView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user/register.html')

    def post(self, request, *args, **kwargs):
        # TODO: Implement register logic
        return redirect('user-login')

class LogoutView(View):
    def post(self, request, *args, **kwargs):
        auth.logout(request)
        return redirect('user-login')
