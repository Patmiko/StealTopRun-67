from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('user/login', views.LoginView.as_view(), name='user-login'),
    path('user/register', views.RegisterView.as_view(), name='user-register'),
    path('user/logout', views.LogoutView.as_view(), name='user-logout'),
    path('user/<str:username>/', views.UserProfileView.as_view(), name='user-profile'),


    path('games/', views.GamesView.as_view(), name='game-list'),
    
    path('games/<int:game_id>/', views.GameDetailView.as_view(), name='game-detail'),

    path('games/<int:game_id>/speedrun-types/<int:type_id>/speedruns/<int:speedrun_id>/', views.SpeedrunDetailView.as_view(), name='speedrun-view'),
    path('games/<int:game_id>/speedrun-types/<int:type_id>/speedruns/', views.SpeedrunUploadView.as_view(), name='speedrun-upload'),

    
]