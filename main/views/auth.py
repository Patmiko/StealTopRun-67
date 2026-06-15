from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.views import View
from ..models import User, Speedrun, VerificationStatus
from ..forms import UserProfileEditForm, RegisterForm
from django.core import signing
from django.contrib.auth.mixins import LoginRequiredMixin
from ..utils import send_verification_email, send_change_email, send_security_alert_email, send_password_reset_email


class LoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user/login.html')

    def post(self, request, *args, **kwargs):
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')

        user = None

        if '@' in username_or_email:
            # Try to find the user by email
            try:
                user_obj = User.objects.get(email=username_or_email)
                username = user_obj.username
                user = authenticate(request, username=username, password=password)
            except User.DoesNotExist:
                user = None
        else:
            # Otherwise, authenticate by username normally
            user = authenticate(request, username=username_or_email, password=password)

        if user is not None and user.status != VerificationStatus.VERIFIED:
            if user.status == VerificationStatus.UNVERIFIED:
                messages.error(request, 'Your email is not verified. Please check your inbox for the verification link.')
                return render(request, 'email_resend.html')
            else:
                messages.error(request, 'This account is inaccessible')
                return render(request, 'user/login.html')

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username/email or password.')
            return render(request, 'user/login.html')


class RegisterView(View):
    def get(self, request, *args, **kwargs):
        form = RegisterForm()
        return render(request, 'user/register.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.status = VerificationStatus.UNVERIFIED
            user.save()
            try:
                send_verification_email(request, user)
                messages.success(request, 'Verification email sent! Please check your inbox to verify your account.')
                return redirect('verification-pending')
            except Exception:
                messages.error(request, f'Error sending verification email. Please resend the verification email.')
                return render(request, 'email_resend.html')

        return render(request, 'user/register.html', {'form': form})


class LogoutView(LoginRequiredMixin, View):
    login_url = 'user-login'

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('user-login')


class UserProfileView(View):
    def get(self, request, username, *args, **kwargs):
        profile_user = get_object_or_404(User, username=username)

        if profile_user.status != VerificationStatus.VERIFIED:
            messages.error(request, 'No valid user with that username found')
            return redirect('home')

        user_runs = Speedrun.objects.filter(user=profile_user, status='ACCEPTED').select_related('speedrun_type', 'speedrun_type__game')

        context = {
            'profile_user': profile_user,
            'user_runs': user_runs,
        }
        return render(request, 'user/profile.html', context)


class EditUserProfileView(LoginRequiredMixin, View):
    login_url = 'user-login'

    def get(self, request, username, *args, **kwargs):
        profile_user = get_object_or_404(User, username=username)

        if request.user != profile_user:
            messages.error(request, "You cannot edit someone else's profile.")
            return redirect('user-profile', username=profile_user.username)

        profile_form = UserProfileEditForm(instance=profile_user)
        password_form = PasswordChangeForm(user=profile_user)

        context = {
            'profile_user': profile_user,
            'profile_form': profile_form,
            'password_form': password_form,
            'pending_email': request.session.get('pending_email'),
        }
        return render(request, 'user/edit-profile.html', context)

    def post(self, request, username, *args, **kwargs):
        profile_user = get_object_or_404(User, username=username)

        if request.user != profile_user:
            messages.error(request, "You cannot edit someone else's profile.")
            return redirect('user-profile', username=profile_user.username)

        original_email = profile_user.email

        action = request.POST.get('action')
        profile_form = UserProfileEditForm(instance=profile_user)
        password_form = PasswordChangeForm(user=profile_user)

        if action == 'update_profile':
            profile_form = UserProfileEditForm(request.POST, request.FILES, instance=profile_user)
            if profile_form.is_valid():
                user_instance = profile_form.save(commit=False)

                new_username = profile_form.cleaned_data.get('username')
                new_email = profile_form.cleaned_data.get('email')

                has_errors = False
                if User.objects.filter(username=new_username).exclude(pk=profile_user.pk).exists():
                    profile_form.add_error('username', 'This username is already taken.')
                    has_errors = True

                if User.objects.filter(email=new_email).exclude(pk=profile_user.pk).exists():
                    profile_form.add_error('email', 'This email is already taken.')
                    has_errors = True

                if not has_errors:
                    user_instance.username = new_username

                    if new_email != original_email:

                        user_instance.email = original_email
                        profile_user.email = original_email
                        try:
                            send_change_email(request, profile_user, original_email, new_email)
                            send_security_alert_email(request, profile_user, new_email)
                            request.session['pending_email'] = original_email
                            messages.info(request, 'A verification link has been sent to your new email. Please verify to complete the change.')
                        except Exception:
                            messages.error(request, 'Error sending verification email. Please try again later.')
                            return redirect('edit-profile', username=profile_user.username)
                    else:
                        user_instance.email = original_email

                    user_instance.save()
                    profile_form.save_m2m()

                    messages.success(request, 'Profile updated successfully!')
                    return redirect('user-profile', username=user_instance.username)
            else:
                messages.error(request, 'Please correct the errors in the profile form.')

        elif action == 'change_password':
            password_form = PasswordChangeForm(user=profile_user, data=request.POST)
            if password_form.is_valid():
                # Extract the validated new password
                new_password = password_form.cleaned_data.get('new_password1')

                # Sign the password so it can be passed in the URL
                signed_password = signing.dumps(new_password)

                # Pass the signed password as a target to your email utility
                try:
                    send_password_reset_email(request, profile_user, target=signed_password)
                except Exception:
                    messages.error(request, 'Error sending password confirmation email. Please try again later.')
                    return redirect('edit-profile', username=profile_user.username)

                messages.info(request, 'A password confirmation link has been sent to your email. Please check your inbox to finalize the change and login with your new password.')
                logout(request)
                return redirect('user-login')
            else:
                messages.error(request, 'Please correct the errors in the password form.')

        context = {
            'profile_user': profile_user,
            'profile_form': profile_form,
            'password_form': password_form,
            'pending_email': request.session.get('pending_email'),
        }
        return render(request, 'user/edit-profile.html', context)


class SearchUserView(View):
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('q', '').strip()

        if search_query:
            users = User.objects.filter(username__icontains=search_query)
            users = users.filter(status='VERIFIED')
        else:
            users = User.objects.none()

        return render(request, 'user/search_users.html', {'users': users, 'search_term': search_query})


class DeleteUserView(LoginRequiredMixin, View):
    login_url = 'user-login'

    def post(self, request, *args, **kwargs):
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('home')
