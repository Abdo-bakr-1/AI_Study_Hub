"""Core models shared across the application."""

from django.conf import settings
from django.db import models
from django.utils import timezone


class ActivityLog(models.Model):
    """Records user actions for the dashboard "Recent Activity" feed.

    Maps to the ``activity_log`` table in the ERD.
    """

    class Action(models.TextChoices):
        CREATED = "created", "Created"
        UPDATED = "updated", "Updated"
        DELETED = "deleted", "Deleted"
        COMPLETED = "completed", "Completed"
        REOPENED = "reopened", "Reopened"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activity_logs",
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    content_type = models.CharField(
        max_length=50,
        help_text="The kind of object this activity relates to (task, note, ...).",
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Activity log"
        verbose_name_plural = "Activity logs"

    def __str__(self):
        return f"{self.user} {self.action} {self.content_type}"

    @classmethod
    def log(cls, user, action, content_type, description, object_id=None):
        """Convenience helper to record an activity entry."""
        return cls.objects.create(
            user=user,
            action=action,
            content_type=content_type,
            description=description,
            object_id=object_id,
        )
