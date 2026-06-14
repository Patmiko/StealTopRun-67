from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core import signing

def send_verification_email(request, user):
    """
    Generates a token and sends a HTML verification email.
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    domain = request.get_host()

    verification_path = reverse('verify-email', kwargs={'uidb64': uid, 'token': token})
    verification_url = f"http://{domain}{verification_path}"

    subject = "Verify your Speedrun Tracker Account"
    
    context = {
        'username': user.username,
        'verification_url': verification_url,
    }
    
    html_message = render_to_string('emails/verification_email.html', context)
    
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_change_email(request, user, new_email):
    """
    Generates a token, securely signs the new email string, 
    and sends a HTML verification email directly to the new address.
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    domain = request.get_host()

    signed_email = signing.dumps(new_email)

    verification_path = reverse('change-email', kwargs={'uidb64': uid, 'token': token})
    
    change_email_url = f"http://{domain}{verification_path}?target={signed_email}"

    subject = "Verify your new email for Speedrun Tracker"
    
    context = {
        'username': user.username,
        'change_email_url': change_email_url,
        'new_email': new_email,
    }
    
    html_message = render_to_string('emails/change_email.html', context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[new_email],
        html_message=html_message,
        fail_silently=False,
    )

def send_security_alert_email(request, user, old_email, new_email):
    """
    Sends a security alert to the user's original email address notifying them
    that an email change has been requested.
    """
    domain = request.get_host()

    subject = "Security Alert: Email change requested on StealTopRun"
    
    context = {
        'username': user.username,
        'new_email': new_email,
    }
    
    html_message = render_to_string('emails/security_alert_email.html', context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[old_email], 
        html_message=html_message,
        fail_silently=False,
    )