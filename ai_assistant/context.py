"""Builds optional study context passed to the AI service.

All database access stays inside Django and is strictly scoped to the current
user, so the assistant can never see another user's data.
"""

from django.utils import timezone

from notes.models import Note
from planner.models import Task


def build_user_context(user):
    """Return a short text summary of the user's own study data."""
    today = timezone.now().date()

    pending = (
        Task.objects.filter(user=user, is_completed=False)
        .order_by("due_date")[:10]
    )
    recent_notes = Note.objects.filter(user=user).order_by("-updated_at")[:5]

    lines = []

    if pending:
        lines.append("Pending tasks:")
        for task in pending:
            due = (
                f" (due {task.due_date:%Y-%m-%d}"
                + (", OVERDUE" if task.due_date and task.due_date < today else "")
                + ")"
                if task.due_date
                else ""
            )
            lines.append(f"- [{task.get_priority_display()}] {task.title}{due}")
    else:
        lines.append("The user has no pending tasks.")

    if recent_notes:
        lines.append("")
        lines.append("Recent note titles:")
        for note in recent_notes:
            lines.append(f"- {note.title}")

    return "\n".join(lines)
