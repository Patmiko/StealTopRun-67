from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q, Prefetch
from django.views import View
from ..models import User, Game, Speedrun, SpeedrunType, VerificationStatus
from ..forms import Category, ResendVerificationForm, SpeedrunForm, GameRequestForm, SpeedrunTypeRequestForm, UserReportForm, SpeedrunReportForm, UserProfileEditForm, RegisterForm
import json
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.core import signing
from ..utils import send_verification_email, send_change_email, send_security_alert_email, send_password_reset_email

# SPEEDRUN TYPES PATHS
# ===================================================================================================================


class CategoryLeaderboardView(LoginRequiredMixin, View):
    login_url = 'user-login'

    def get(self, request, game_id, type_id, *args, **kwargs):
        game = get_object_or_404(Game, pk=game_id)
        category = get_object_or_404(SpeedrunType, pk=type_id, game=game)

        speedruns = Speedrun.objects.filter(
            speedrun_type=category,
            status='ACCEPTED',
            user__status=VerificationStatus.VERIFIED
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
                    'formatted': format_seconds(best_time)
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

# SPEEDRUN PATHS
# ===================================================================================================================


class SpeedrunDetailView(LoginRequiredMixin, View):
    login_url = 'user-login'

    def get(self, request, game_id, type_id, speedrun_id, *args, **kwargs):
        game = get_object_or_404(Game, pk=game_id)
        category = get_object_or_404(SpeedrunType, pk=type_id, game=game)

        speedrun = get_object_or_404(
            Speedrun,
            pk=speedrun_id,
            speedrun_type=category,
            user__status=VerificationStatus.VERIFIED
        )

        rank = Speedrun.objects.filter(
            speedrun_type=category,
            status='ACCEPTED',
            user__status=VerificationStatus.VERIFIED,
            time__lt=speedrun.time,
        ).count() + 1

        return render(request, 'speedrun_detail.html', {
            'game': game,
            'category': category,
            'speedrun': speedrun,
            'rank': rank
        })


class SpeedrunUploadView(LoginRequiredMixin, View):
    login_url = 'user-login'

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


class SpeedrunDeleteView(LoginRequiredMixin, View):
    def post(self, request, game_id, type_id, speedrun_id, *args, **kwargs):
        speedrun = get_object_or_404(Speedrun, pk=speedrun_id, speedrun_type__id=type_id)

        # Security check: ensure only the owner can delete
        if request.user == speedrun.user:
            speedrun.delete()
            messages.success(request, 'Speedrun deleted successfully.')
        else:
            messages.error(request, 'You do not have permission to delete this run.')

        return redirect('category-leaderboard', game_id=game_id, type_id=type_id)
