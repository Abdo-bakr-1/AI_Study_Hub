"""Dashboard view: statistics, charts data and recent activity."""

import json

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone

from ai_assistant.models import Conversation
from core.models import ActivityLog
from notes.models import Note, NoteCategory
from planner.models import Task
from resources.models import Resource


@login_required
def home(request):
    user = request.user

    # --- Task statistics -------------------------------------------------
    tasks = Task.objects.filter(user=user)
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(is_completed=True).count()
    pending_tasks = total_tasks - completed_tasks

    total_notes = Note.objects.filter(user=user).count()
    total_resources = Resource.objects.filter(user=user).count()
    total_conversations = Conversation.objects.filter(user=user).count()

    # --- Tasks by priority (only pending count towards "to do") ----------
    priority_counts = {
        "low": tasks.filter(priority=Task.Priority.LOW).count(),
        "medium": tasks.filter(priority=Task.Priority.MEDIUM).count(),
        "high": tasks.filter(priority=Task.Priority.HIGH).count(),
    }

    # --- Notes by category ----------------------------------------------
    note_categories = (
        NoteCategory.objects.filter(user=user)
        .annotate(count=Count("notes"))
        .order_by("-count")[:8]
    )
    notes_by_category_labels = [c.name for c in note_categories]
    notes_by_category_values = [c.count for c in note_categories]
    # Notes with no category at all.
    uncategorized_notes = Note.objects.filter(user=user, categories__isnull=True).count()
    if uncategorized_notes:
        notes_by_category_labels.append("Uncategorized")
        notes_by_category_values.append(uncategorized_notes)

    # --- Upcoming & overdue tasks ---------------------------------------
    today = timezone.now().date()
    upcoming_tasks = (
        tasks.filter(is_completed=False, due_date__gte=today)
        .order_by("due_date")[:5]
    )
    overdue_tasks = tasks.filter(is_completed=False, due_date__lt=today).count()

    # --- Recent activity -------------------------------------------------
    recent_activity = ActivityLog.objects.filter(user=user)[:10]

    # Flat keys consumed by static/js/charts.js.
    charts = {
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "priority_low": priority_counts["low"],
        "priority_medium": priority_counts["medium"],
        "priority_high": priority_counts["high"],
        "notes_categories": notes_by_category_labels,
        "notes_category_counts": notes_by_category_values,
    }

    context = {
        "stats": {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "total_notes": total_notes,
            "total_resources": total_resources,
            "total_conversations": total_conversations,
            "overdue_tasks": overdue_tasks,
        },
        "upcoming_tasks": upcoming_tasks,
        "recent_activity": recent_activity,
        "charts_json": json.dumps(charts),
    }
    return render(request, "dashboard/home.html", context)
