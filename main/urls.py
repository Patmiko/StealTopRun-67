from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('user/login', views.LoginView.as_view(), name='user-login'),
    path('user/register', views.RegisterView.as_view(), name='user-register'),
    path('user/logout', views.LogoutView.as_view(), name='user-logout'),

    path('game/', views.GameListView.as_view(), name='game-list'),
    path('game/<str:name>/', views.GameSearchView.as_view(), name='game-search'),
    path('game/add/', views.GameCreateView.as_view(), name='game-add'), # Admin only
    path('game/<int:game_id>/edit/', views.GameEditView.as_view(), name='game-edit'), # Admin only

    path('speedrunType/', views.SpeedrunTypeCreateView.as_view(), name='speedrun-type-add'), # Admin only
    path('speedrunType/<int:speedrunType_id>/', views.SpeedrunTypeEditView.as_view(), name='speedrun-type-edit'), # Admin only
    path('speedrunType/<int:game_id>/', views.SpeedrunTypeListView.as_view(), name='speedrun-type-list'),

    path('speedrun/submit', views.SpeedrunUploadView.as_view(), name='speedrun-submit'),
]