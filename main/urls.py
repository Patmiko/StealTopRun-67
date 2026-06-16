from django.urls import path
import main.views.auth as auth_views
import main.views.games as games_views
import main.views.speedruns as speedrun_views
import main.views.interactions as interactions_views
import main.views.core as core_views
import main.views.verification as verification_views

urlpatterns = [
    # Core
    path('', core_views.HomeView.as_view(), name='home'),
    path('contact/', core_views.ContactView.as_view(), name='contact'),


    # User Auth & Profiles
    path('user/login', auth_views.LoginView.as_view(), name='user-login'),
    path('user/register', auth_views.RegisterView.as_view(), name='user-register'),
    path('user/logout', auth_views.LogoutView.as_view(), name='user-logout'),
    path('user/<str:username>/', auth_views.UserProfileView.as_view(), name='user-profile'),
    path('user/<str:username>/edit/', auth_views.EditUserProfileView.as_view(), name='edit-profile'),
    path('user/delete', auth_views.DeleteUserView.as_view(), name='delete-profile'),
    path('users/search/', auth_views.SearchUserView.as_view(), name='user-search'),

    # Email Verification
    path('verify-email/<str:uidb64>/<str:token>/', verification_views.EmailVerificationView.as_view(), name='verify-email'),
    path('resend-verification/', verification_views.ResendVerificationEmailView.as_view(), name='resend-verification'),
    path('verify-pending/', verification_views.verificationPendingView.as_view(), name='verification-pending'),
    # Email Change Verification
    path('change-email/<str:uidb64>/<str:token>/', verification_views.ChangeEmailView.as_view(), name='change-email'),
    # Password Reset Request
    path('forgot-password/', verification_views.RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('reset-password/<str:token>/', verification_views.ResetPasswordView.as_view(), name='reset-password'),


    # Games & Leaderboards
    path('games/', games_views.GamesView.as_view(), name='game-list'),
    path('games/<int:game_id>/', games_views.GameDetailView.as_view(), name='game-detail'),
    path('discover/', games_views.DiscoverView.as_view(), name='discover'),

    # Speedruns
    path('games/<int:game_id>/speedrun-types/<int:type_id>/', speedrun_views.CategoryLeaderboardView.as_view(), name='category-leaderboard'),
    path('games/<int:game_id>/speedrun-types/<int:type_id>/speedruns/<int:speedrun_id>/', speedrun_views.SpeedrunDetailView.as_view(), name='speedrun-view'),
    path('games/<int:game_id>/speedrun-types/<int:type_id>/speedruns/', speedrun_views.SpeedrunUploadView.as_view(), name='speedrun-upload'),
    path('games/<int:game_id>/speedrun-types/<int:type_id>/speedruns/<int:speedrun_id>/delete/',
         speedrun_views.SpeedrunDeleteView.as_view(), name='speedrun-delete'),

    # Requests
    path('requests/submit/', interactions_views.RequestSubmissionView.as_view(), name='request-submit'),

    # Reports
    path('user/<str:username>/report/', interactions_views.ReportUserView.as_view(), name='report-user'),
    path('speedruns/<int:speedrun_id>/report/', interactions_views.ReportSpeedrunView.as_view(), name='report-speedrun'),

    # Error Handling
    path('404/', core_views.PageNotFoundView.as_view(), name='page-not-found'),
    path('500/', core_views.ServerErrorView.as_view(), name='server-error'),
    path('403/', core_views.PermissionDeniedView.as_view(), name='permission-denied'),
    path('400/', core_views.BadRequestView.as_view(), name='bad-request'),
]