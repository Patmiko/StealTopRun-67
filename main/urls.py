from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('user/login', views.LoginView.as_view(), name='user-login'),
    path('user/register', views.RegisterView.as_view(), name='user-register'),
    path('user/logout', views.LogoutView.as_view(), name='user-logout'),
]