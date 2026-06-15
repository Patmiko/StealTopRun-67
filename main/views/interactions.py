from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from ..models import User, Speedrun
from ..forms import GameRequestForm, SpeedrunTypeRequestForm, UserReportForm, SpeedrunReportForm
from django.contrib.auth.mixins import LoginRequiredMixin


# REQUESTS PATHS
# ===================================================================================================================

class RequestSubmissionView(LoginRequiredMixin, View):
    login_url = 'user-login'

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


# REPORTS PATHS
# ===================================================================================================================

class ReportUserView(LoginRequiredMixin, View):
    login_url = 'user-login'

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


class ReportSpeedrunView(LoginRequiredMixin, View):
    login_url = 'user-login'

    def get(self, request, speedrun_id, *args, **kwargs):
        target_run = get_object_or_404(Speedrun, pk=speedrun_id)

        form = SpeedrunReportForm()
        return render(request, 'report_form.html', {
            'form': form,
            'target_name': f"{target_run.speedrun_type.game.name} - {target_run.formatted_time}s by {target_run.user.username}",
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
