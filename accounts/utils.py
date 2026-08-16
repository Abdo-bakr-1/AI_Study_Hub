"""Email helpers for verification and password reset."""

import logging

import requests
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

logger = logging.getLogger(__name__)


def _absolute_url(request, url_name, token):
    path = reverse(url_name, args=[token])
    return request.build_absolute_uri(path)


def _send_via_brevo_api(subject, html_content, text_content, to_email, to_name):
    """Send an email via Brevo's transactional email API.

    Returns True if successful, False otherwise.
    """
    api_key = getattr(settings, "BREVO_API_KEY", "")
    if not api_key:
        logger.error("BREVO_API_KEY not configured; cannot send email to %s", to_email)
        return False

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "AI Study Hub <no-reply@aistudyhub.local>")
    # Parse "Name <email>" format if present
    if "<" in from_email and ">" in from_email:
        from_name = from_email.split("<")[0].strip()
        from_addr = from_email.split("<")[1].split(">")[0].strip()
    else:
        from_name = "AI Study Hub"
        from_addr = from_email

    payload = {
        "sender": {"name": from_name, "email": from_addr},
        "to": [{"email": to_email, "name": to_name}],
        "subject": subject,
        "htmlContent": html_content,
        "textContent": text_content,
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=10,
        )
        if response.status_code == 201:
            return True
        else:
            logger.error(
                "Brevo API error for %s: %s %s",
                to_email,
                response.status_code,
                response.text[:500],
            )
            return False
    except requests.exceptions.Timeout:
        logger.error("Brevo API timeout sending to %s", to_email)
        return False
    except requests.exceptions.RequestException as e:
        logger.error("Brevo API request failed for %s: %s", to_email, e)
        return False


def send_verification_email(request, user, verification):
    """Send the email verification link via Brevo API (or console in dev).

    Returns True if the email was sent successfully, False otherwise.
    Never fails silently in production - email delivery problems are logged.
    """
    link = _absolute_url(request, "accounts:verify_email", verification.token)
    subject = "Verify your AI Study Hub account"
    text_content = (
        f"Hi {user.username},\n\n"
        "Thanks for registering at AI Study Hub!\n\n"
        "Please verify your email address by clicking the link below:\n"
        f"{link}\n\n"
        "This link will expire in 48 hours.\n\n"
        "If you did not create this account you can ignore this email."
    )
    html_content = (
        f"<p>Hi {user.username},</p>"
        "<p>Thanks for registering at AI Study Hub!</p>"
        "<p>Please verify your email address by clicking the link below:</p>"
        f"<p><a href=\"{link}\">Verify your email address</a></p>"
        "<p>This link will expire in 48 hours.</p>"
        "<p>If you did not create this account you can ignore this email.</p>"
    )

    # In development, use console backend if configured
    email_backend = getattr(settings, "EMAIL_BACKEND", "")
    if email_backend == "django.core.mail.backends.console.EmailBackend":
        # Print to console for development
        logger.info("=== DEV EMAIL (verification) ===")
        logger.info("To: %s", user.email)
        logger.info("Subject: %s", subject)
        logger.info("Body:\n%s", text_content)
        logger.info("=== END DEV EMAIL ===")
        return True

    return _send_via_brevo_api(subject, html_content, text_content, user.email, user.username)


def send_password_reset_email(request, user, token):
    """Send the password reset link via Brevo API (or console in dev).

    Returns True if the email was sent successfully, False otherwise.
    """
    link = _absolute_url(request, "accounts:password_reset_confirm", token.token)
    subject = "Reset your AI Study Hub password"
    text_content = (
        f"Hi {user.username},\n\n"
        "We received a request to reset your password.\n\n"
        "Click the link below to choose a new password:\n"
        f"{link}\n\n"
        "This link will expire in 1 hour.\n\n"
        "If you did not request a password reset you can ignore this email."
    )
    html_content = (
        f"<p>Hi {user.username},</p>"
        "<p>We received a request to reset your password.</p>"
        "<p>Click the link below to choose a new password:</p>"
        f"<p><a href=\"{link}\">Reset your password</a></p>"
        "<p>This link will expire in 1 hour.</p>"
        "<p>If you did not request a password reset you can ignore this email.</p>"
    )

    # In development, use console backend if configured
    email_backend = getattr(settings, "EMAIL_BACKEND", "")
    if email_backend == "django.core.mail.backends.console.EmailBackend":
        # Print to console for development
        logger.info("=== DEV EMAIL (password reset) ===")
        logger.info("To: %s", user.email)
        logger.info("Subject: %s", subject)
        logger.info("Body:\n%s", text_content)
        logger.info("=== END DEV EMAIL ===")
        return True

    return _send_via_brevo_api(subject, html_content, text_content, user.email, user.username)
