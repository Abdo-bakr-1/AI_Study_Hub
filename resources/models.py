"""Learning resources models: ResourceCategory and Resource."""

from django.conf import settings
from django.db import models
from django.urls import reverse


class ResourceCategory(models.Model):
    """A user-owned category used to group learning resources.

    Maps to the ``resource_category`` table.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resource_categories",
    )
    name = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("user", "name")
        verbose_name_plural = "Resource categories"

    def __str__(self):
        return self.name


class Resource(models.Model):
    """A saved learning resource (link) owned by a user.

    Maps to the ``resource`` table with a Many-to-Many relationship to
    ``ResourceCategory`` (resource_category M2M table in the ERD).
    """

    class ResourceType(models.TextChoices):
        ARTICLE = "article", "Article"
        VIDEO = "video", "Video"
        DOCUMENTATION = "documentation", "Documentation"
        COURSE = "course", "Course"
        BOOK = "book", "Book"
        WEBSITE = "website", "Website"
        OTHER = "other", "Other"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resources",
    )
    categories = models.ManyToManyField(
        ResourceCategory,
        blank=True,
        related_name="resources",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    link = models.URLField(max_length=500)
    resource_type = models.CharField(
        max_length=20,
        choices=ResourceType.choices,
        default=ResourceType.ARTICLE,
    )
    thumbnail = models.ImageField(upload_to="resources/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("resources:detail", args=[self.pk])
