"""Study planner models: TaskCategory and Task."""

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class TaskCategory(models.Model):
    """A user-owned category used to group tasks.

    Maps to the ``task_category`` table (One Category -> Many Tasks).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="task_categories",
    )
    name = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("user", "name")
        verbose_name_plural = "Task categories"

    def __str__(self):
        return self.name


class Task(models.Model):
    """A single study task owned by a user.

    Maps to the ``task`` table. A task belongs to one user and, through the
    Many-to-Many ``categories`` field, can be filed under several categories
    (satisfying the ERD's task_category M2M relationship).
    """

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    categories = models.ManyToManyField(
        TaskCategory,
        blank=True,
        related_name="tasks",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["is_completed", "-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("planner:task_detail", args=[self.pk])

    # -- Status helpers ----------------------------------------------------
    def mark_completed(self):
        self.is_completed = True
        self.status = self.Status.COMPLETED
        self.save(update_fields=["is_completed", "status", "updated_at"])

    def mark_pending(self):
        self.is_completed = False
        self.status = self.Status.PENDING
        self.save(update_fields=["is_completed", "status", "updated_at"])

    def toggle(self):
        if self.is_completed:
            self.mark_pending()
        else:
            self.mark_completed()

    @property
    def is_overdue(self):
        return (
            not self.is_completed
            and self.due_date is not None
            and self.due_date < timezone.now().date()
        )

    @property
    def priority_rank(self):
        return {"high": 3, "medium": 2, "low": 1}.get(self.priority, 0)
