"""Authentication, profile, email verification and password reset views."""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import (
    LoginForm,
    PasswordResetRequestForm,
    ProfileForm,
    RegisterForm,
    ResendVerificationForm,
    SetNewPasswordForm,
    StyledPasswordChangeForm,
    UserForm,
)
from .models import EmailVerification, PasswordResetToken, Profile
from .utils import send_password_reset_email, send_verification_email


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            verification = EmailVerification.objects.create(user=user)
            if settings.EMAIL_VERIFICATION_REQUIRED:
                email_sent = send_verification_email(request, user, verification)
                if email_sent:
                    messages.success(
                        request,
                        "Account created! Check your email to verify your account "
                        "before logging in.",
                    )
                else:
                    # Email failed to send - keep user inactive, inform them
                    messages.error(
                        request,
                        "Account created, but we couldn't send the verification email. "
                        "Please try again later or contact support. Your account "
                        "will remain inactive until verified.",
                    )
            else:
                # Verification disabled (e.g. live demo without SMTP): the
                # account is usable immediately.
                verification.is_verified = True
                verification.save(update_fields=["is_verified"])
                user.is_active = True
                user.save(update_fields=["is_active"])
                messages.success(request, "Account created! You can now log in.")
            return redirect("accounts:login")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


def verify_email(request, token):
    verification = get_object_or_404(EmailVerification, token=token)
    if verification.is_verified:
        messages.info(request, "This email is already verified. You can log in.")
        return redirect("accounts:login")
    if verification.is_expired:
        messages.error(
            request,
            "This verification link has expired. Please register again or "
            "request a new link.",
        )
        return redirect("accounts:login")

    verification.is_verified = True
    verification.save(update_fields=["is_verified"])
    user = verification.user
    user.is_active = True
    user.save(update_fields=["is_active"])
    messages.success(request, "Email verified! You can now log in.")
    return redirect("accounts:login")


def resend_verification(request):
    """Resend a verification email for an unverified account.

    A simple rate limit (cooldown) prevents email spam.
    """
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        form = ResendVerificationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = User.objects.filter(
                email__iexact=email, is_active=False
            ).first()
            if user:
                # Find the latest pending verification record.
                pending = (
                    EmailVerification.objects.filter(user=user, is_verified=False)
                    .order_by("-created_at")
                    .first()
                )
                # Rate limit: only resend if last attempt was > 60s ago.
                if pending and not pending.is_expired:
                    age = (timezone.now() - pending.created_at).total_seconds()
                    if age < 60:
                        messages.warning(
                            request,
                            "Please wait a moment before requesting another "
                            "verification email.",
                        )
                        return redirect("accounts:login")

                # Invalidate old pending tokens, create a fresh one.
                EmailVerification.objects.filter(
                    user=user, is_verified=False
                ).update(is_verified=True)
                verification = EmailVerification.objects.create(user=user)
                send_verification_email(request, user, verification)
                messages.success(
                    request,
                    "If an account exists for that email, a new verification "
                    "link has been sent.",
                )
            else:
                # Always show the same message to avoid leaking emails.
                messages.success(
                    request,
                    "If an account exists for that email, a new verification "
                    "link has been sent.",
                )
            return redirect("accounts:login")
    else:
        form = ResendVerificationForm()
    return render(
        request,
        "registration/resend_verification.html",
        {"form": form},
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, f"Welcome back, {request.user.username}!")
            # Only allow same-site "next" targets to avoid open redirects.
            next_url = request.GET.get("next")
            if not url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                next_url = None
            return redirect(next_url or "dashboard:home")
        # Distinguish an unverified (inactive) account for a friendlier message.
        username = request.POST.get("username", "")
        if User.objects.filter(username=username, is_active=False).exists():
            messages.warning(
                request,
                "Your account is not verified yet. Please check your email.",
            )
    else:
        form = LoginForm(request)
    return render(request, "registration/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("accounts:login")


@login_required
def profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(
            request.POST, request.FILES, instance=profile_obj
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("accounts:profile")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=profile_obj)

    return render(
        request,
        "accounts/profile.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "profile": profile_obj,
        },
    )


@login_required
def change_password(request):
    if request.method == "POST":
        form = StyledPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been changed.")
            return redirect("accounts:profile")
    else:
        form = StyledPasswordChangeForm(request.user)
    return render(request, "accounts/change_password.html", {"form": form})


# --- Custom password reset flow ------------------------------------------
def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = User.objects.filter(email__iexact=email).first()
            if user:
                token = PasswordResetToken.objects.create(user=user)
                email_sent = send_password_reset_email(request, user, token)
                if not email_sent:
                    messages.error(
                        request,
                        "We encountered an issue sending the reset email. "
                        "Please try again later.",
                    )
            # Always show the same message to avoid leaking which emails exist.
            messages.success(
                request,
                "If an account exists for that email, a password reset link "
                "has been sent. (In development it is printed to the console.)",
            )
            return redirect("accounts:login")
    else:
        form = PasswordResetRequestForm()
    return render(request, "registration/password_reset_request.html", {"form": form})


def password_reset_confirm(request, token):
    reset_token = get_object_or_404(PasswordResetToken, token=token)
    if not reset_token.is_valid:
        messages.error(
            request, "This password reset link is invalid or has expired."
        )
        return redirect("accounts:password_reset_request")

    if request.method == "POST":
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            user = reset_token.user
            user.set_password(form.cleaned_data["new_password1"])
            user.save()
            reset_token.is_used = True
            reset_token.save(update_fields=["is_used"])
            messages.success(
                request, "Your password has been reset. You can now log in."
            )
            return redirect("accounts:login")
    else:
        form = SetNewPasswordForm()
    return render(
        request,
        "registration/password_reset_confirm.html",
        {"form": form, "token": token},
    )
