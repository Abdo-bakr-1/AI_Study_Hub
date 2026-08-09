"""Notes models: NoteCategory and Note."""

from django.conf import settings
from django.db import models
from django.urls import reverse


class NoteCategory(models.Model):
    """A user-owned category used to group notes.

    Maps to the ``note_category`` table.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="note_categories",
    )
    name = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("user", "name")
        verbose_name_plural = "Note categories"

    def __str__(self):
        return self.name


class Note(models.Model):
    """A study note owned by a user.

    Maps to the ``note`` table. Uses a Many-to-Many relationship with
    ``NoteCategory`` (the note_category M2M table in the ERD).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notes",
    )
    categories = models.ManyToManyField(
        NoteCategory,
        blank=True,
        related_name="notes",
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to="notes/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("notes:detail", args=[self.pk])

    @property
    def excerpt(self):
        text = self.content.strip()
        return text if len(text) <= 160 else text[:157] + "..."
