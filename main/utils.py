from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings

def send_verification_email(request, user):
    """
    Generates a cryptographically signed, one-time-use token 
    and sends a verification email to the user.
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    token = default_token_generator.make_token(user)

    domain = request.get_host()

    verification_path = reverse('verify-email', kwargs={'uidb64': uid, 'token': token})

    verification_url = f"http://{domain}{verification_path}"

    subject = "Verify your Speedrun Tracker Account"
    message = (
        f"Hi {user.username},\n\n"
        f"Thank you for registering! Please click the link below to verify your email address:\n\n"
        f"{verification_url}\n\n"
        f"This link will expire in a few hours."
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,  # If something is wrong with your SMTP config, this will raise an error so you know about it
    )