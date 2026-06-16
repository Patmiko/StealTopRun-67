from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash, get_user_model
from django.contrib import messages
from django.views import View
from ..models import User, VerificationStatus
from ..forms import ResendVerificationForm, PasswordResetRequestForm
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.core import signing
from ..utils import send_verification_email, send_password_reset_email


class EmailVerificationView(View):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.status = VerificationStatus.VERIFIED
            user.save()
            messages.success(request, 'Your email has been verified! You can now log in.')
            return render(request, 'user/login.html')
        else:
            messages.error(request, 'Invalid or expired verification link. Please request a new one.')
            return render(request, 'email_resend.html')


class ResendVerificationEmailView(View):
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'email_resend.html', {'error': 'If that email is registered and unverified, a new link has been sent.'})

        # Check if already verified
        if user.status == VerificationStatus.VERIFIED:
            return render(request, 'email_resend.html', {'error': 'This account is already verified.'})

        # Check the Cooldown Cache
        cache_key = f"email_cooldown_{user.pk}"
        if cache.get(cache_key):
            return HttpResponse("Please wait 15 minutes before requesting another email.", status=429)

        try:
            send_verification_email(request, user)
            cache.set(cache_key, True, timeout=900)
        except Exception as e:
            print(f"Email failed to send: {e}")
            return HttpResponse("Error sending email. Please try again later.", status=500)

        return HttpResponse("If that email is registered and unverified, a new link has been sent.")


class verificationPendingView(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.status == VerificationStatus.VERIFIED:
            return redirect('home')

        form = ResendVerificationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.info(request, "If that email is registered and unverified, a new link has been sent.")
                return redirect('verification-pending')

            if user.status == VerificationStatus.VERIFIED:
                messages.warning(request, "This account is already verified. Please log in.")
                return redirect('user-login')

            cache_key = f"email_cooldown_{user.pk}"
            if cache.get(cache_key):
                messages.error(request, "Please wait 15 minutes before requesting another email.")
                return render(request, 'email_resend.html', {'form': form})

            # Send email and trigger cooldown
            try:
                send_verification_email(request, user)
                cache.set(cache_key, True, timeout=900)
                messages.success(request, "A new verification link has been sent to your email.")
            except Exception:
                messages.error(request, "We couldn't send the email right now. Please try again later.")

            return redirect('verification-pending')
        return render(request, 'email_resend.html', {'form': form})

    def get(self, request, *args, **kwargs):
        initial_data = {}
        if request.user.is_authenticated:
            initial_data['email'] = request.user.email
        form = ResendVerificationForm(initial=initial_data)

        return render(request, 'email_resend.html', {'form': form})


class ChangeEmailView(View):
    def get(self, request, uidb64, token, *args, **kwargs):
        User = get_user_model()
        signed_email = request.GET.get('target')

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            new_email = signing.loads(signed_email, max_age=86400)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, 
                signing.BadSignature, signing.SignatureExpired):
            user = None
            new_email = None

        if user is not None and new_email is not None and default_token_generator.check_token(user, token):

            if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
                messages.error(request, "This email address is already registered to another account.")
                return redirect('user-profile', username=user.username)

            user.email = new_email
            user.save()

            if 'pending_email' in request.session:
                del request.session['pending_email']

            messages.success(request, "Your email has been successfully updated!")
            return redirect('user-profile', username=user.username)
        else:
            messages.error(request, "This verification link is invalid or has expired.")
            return redirect('home')


class ResetPasswordView(View):
    def get(self, request, token, *args, **kwargs): 
        User = get_user_model()

        try:
            data = signing.loads(token, max_age=86400)

            user = User.objects.get(pk=data['user_id'])

            new_password = signing.loads(data['password_data'], max_age=86400)

        except (TypeError, ValueError, User.DoesNotExist, signing.BadSignature, signing.SignatureExpired):
            user = None
            new_password = None

        if user is not None and new_password is not None:        
            user.set_password(new_password)
            user.save()

            if 'pending_email' in request.session:
                del request.session['pending_email']

            update_session_auth_hash(request, user)

            messages.success(request, "Your password has been successfully updated!")
            return redirect('user-login')
        else:
            messages.error(request, "This confirmation link is invalid or has expired.")
            return redirect('home')


class RequestPasswordResetView(View):
    def get(self, request, *args, **kwargs):
        form = PasswordResetRequestForm()
        return render(request, 'user/password_reset_request.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']
            
            User = get_user_model()
            try:
                user = User.objects.get(email=email)
                target = signing.dumps(new_password)
                
                send_password_reset_email(request, user, target)
            except User.DoesNotExist:
                pass

            messages.success(request, "A confirmation link has been sent to your email if it exists in our system.")
            return redirect('user-login')
        
        return render(request, 'user/password_reset_request.html', {'form': form})
