from django.urls import path
from . import views

urlpatterns = [
    # Core
    path('', views.HomeView.as_view(), name='home'),
    path('discover/', views.DiscoverView.as_view(), name='discover'),

    # User Auth & Profiles
    path('user/login', views.LoginView.as_view(), name='user-login'),
    path('user/register', views.RegisterView.as_view(), name='user-register'),
    path('user/logout', views.LogoutView.as_view(), name='user-logout'),
    path('user/<str:username>/', views.UserProfileView.as_view(), name='user-profile'),
    path('user/<str:username>/edit/', views.EditUserProfileView.as_view(), name='edit-profile'),
    path('user/delete', views.DeleteUserView.as_view(), name='delete-profile'),
    path('users/search/', views.SearchUserView.as_view(), name='user-search'),

    # Email Verification
    path('verify-email/<str:uidb64>/<str:token>/', views.EmailVerificationView.as_view(), name='verify-email'),
    path('resend-verification/', views.ResendVerificationEmailView.as_view(), name='resend-verification'),
    path('verify-pending/', views.verificationPendingView.as_view(), name='verification-pending'),
    path('reset-password/<str:token>/', views.ResetPasswordView.as_view(), name='reset-password'),
    # Email Change Verification
    path('change-email/<str:uidb64>/<str:token>/', views.ChangeEmailView.as_view(), name='change-email'),


    # Games & Leaderboards
    path('games/', views.GamesView.as_view(), name='game-list'),
    path('games/<int:game_id>/', views.GameDetailView.as_view(), name='game-detail'),
    path('games/<int:game_id>/speedrun-types/<int:type_id>/', views.CategoryLeaderboardView.as_view(), name='category-leaderboard'),

    # Speedruns
    path('games/<int:game_id>/speedrun-types/<int:type_id>/speedruns/<int:speedrun_id>/', views.SpeedrunDetailView.as_view(), name='speedrun-view'),
    path('games/<int:game_id>/speedrun-types/<int:type_id>/speedruns/', views.SpeedrunUploadView.as_view(), name='speedrun-upload'),
    path('games/<int:game_id>/speedrun-types/<int:type_id>/speedruns/<int:speedrun_id>/delete/', 
         views.SpeedrunDeleteView.as_view(), name='speedrun-delete'),
    # Requests
    path('requests/submit/', views.RequestSubmissionView.as_view(), name='request-submit'),

    # Reports
    path('user/<str:username>/report/', views.ReportUserView.as_view(), name='report-user'),
    path('speedruns/<int:speedrun_id>/report/', views.ReportSpeedrunView.as_view(), name='report-speedrun'),

    # Error Handling
    path('404/', views.PageNotFoundView.as_view(), name='page-not-found'),
]