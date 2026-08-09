"""Signals that keep a Profile in sync with the User model."""

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_profile(sender, instance, created, **kwargs):
    """Automatically create a Profile whenever a User is created."""
    if created:
        Profile.objects.create(user=instance)
    else:
        # Ensure a profile always exists (e.g. for users created via shell).
        Profile.objects.get_or_create(user=instance)
