"""Account related models: Profile, EmailVerification, PasswordResetToken."""

import secrets
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


def _generate_token():
    """Return a cryptographically secure URL-safe token."""
    return secrets.token_urlsafe(32)


class Profile(models.Model):
    """Extends the built-in Django User with extra study-profile info.

    Maps to the ``user_profile`` table (One-to-One with auth_user).
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    full_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True,
    )
    date_of_birth = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f"Profile of {self.user.username}"

    @property
    def display_name(self):
        return self.full_name or self.user.get_full_name() or self.user.username

    @property
    def image_url(self):
        """Return the profile image URL or a default placeholder path."""
        if self.profile_picture:
            return self.profile_picture.url
        return settings.STATIC_URL + "images/default-avatar.svg"


class EmailVerification(models.Model):
    """Stores single-use tokens used to verify a user's email address.

    Maps to the ``email_verification`` table.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_verifications",
    )
    token = models.CharField(max_length=64, unique=True, default=_generate_token)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Email verification for {self.user.username}"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at


class PasswordResetToken(models.Model):
    """Stores single-use tokens used for the custom password reset flow.

    Maps to the ``password_reset_token`` table.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
    )
    token = models.CharField(max_length=64, unique=True, default=_generate_token)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Password reset for {self.user.username}"

    @property
    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at
