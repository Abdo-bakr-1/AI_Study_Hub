"""Email helpers for verification and password reset."""

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse


def _absolute_url(request, url_name, token):
    path = reverse(url_name, args=[token])
    return request.build_absolute_uri(path)


def send_verification_email(request, user, verification):
    """Send (or print, in dev) the email verification link."""
    link = _absolute_url(request, "accounts:verify_email", verification.token)
    subject = "Verify your AI Study Hub account"
    body = (
        f"Hi {user.username},\n\n"
        "Thanks for registering at AI Study Hub!\n\n"
        "Please verify your email address by clicking the link below:\n"
        f"{link}\n\n"
        "This link will expire in 48 hours.\n\n"
        "If you did not create this account you can ignore this email."
    )
    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True,
    )


def send_password_reset_email(request, user, token):
    """Send (or print, in dev) the password reset link."""
    link = _absolute_url(request, "accounts:password_reset_confirm", token.token)
    subject = "Reset your AI Study Hub password"
    body = (
        f"Hi {user.username},\n\n"
        "We received a request to reset your password.\n\n"
        "Click the link below to choose a new password:\n"
        f"{link}\n\n"
        "This link will expire in 1 hour.\n\n"
        "If you did not request a password reset you can ignore this email."
    )
    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True,
    )
