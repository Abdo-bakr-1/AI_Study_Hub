"""Views for the study planner (task CRUD, filtering, pagination)."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from core.models import ActivityLog

from .forms import TaskCategoryForm, TaskForm
from .models import Task, TaskCategory

PAGE_SIZE = 10


@login_required
def task_list(request):
    tasks = (
        Task.objects.filter(user=request.user)
        .prefetch_related("categories")
    )

    # --- Filtering -------------------------------------------------------
    status = request.GET.get("status", "").strip()
    priority = request.GET.get("priority", "").strip()
    category_id = request.GET.get("category", "").strip()
    query = request.GET.get("q", "").strip()

    if status in dict(Task.Status.choices):
        tasks = tasks.filter(status=status)
    if priority in dict(Task.Priority.choices):
        tasks = tasks.filter(priority=priority)
    if category_id.isdigit():
        tasks = tasks.filter(categories__id=int(category_id))
    if query:
        tasks = tasks.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    tasks = tasks.distinct()

    paginator = Paginator(tasks, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "tasks": page_obj.object_list,
        "categories": TaskCategory.objects.filter(user=request.user),
        "status_choices": Task.Status.choices,
        "priority_choices": Task.Priority.choices,
        "current_status": status,
        "current_priority": priority,
        "current_category": category_id,
        "query": query,
        "total_count": paginator.count,
    }
    return render(request, "planner/task_list.html", context)


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    return render(request, "planner/task_detail.html", {"task": task})


@login_required
def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save()
            ActivityLog.log(
                request.user,
                ActivityLog.Action.CREATED,
                "task",
                f'Created task "{task.title}"',
                task.pk,
            )
            messages.success(request, "Task created successfully.")
            return redirect("planner:task_detail", pk=task.pk)
    else:
        form = TaskForm(user=request.user)
    return render(
        request,
        "planner/task_form.html",
        {"form": form, "title": "Add Task"},
    )


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            task = form.save()
            ActivityLog.log(
                request.user,
                ActivityLog.Action.UPDATED,
                "task",
                f'Updated task "{task.title}"',
                task.pk,
            )
            messages.success(request, "Task updated successfully.")
            return redirect("planner:task_detail", pk=task.pk)
    else:
        form = TaskForm(instance=task, user=request.user)
    return render(
        request,
        "planner/task_form.html",
        {"form": form, "title": "Edit Task", "task": task},
    )


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == "POST":
        title = task.title
        task.delete()
        ActivityLog.log(
            request.user,
            ActivityLog.Action.DELETED,
            "task",
            f'Deleted task "{title}"',
        )
        messages.success(request, "Task deleted.")
        return redirect("planner:task_list")
    return render(request, "planner/task_confirm_delete.html", {"task": task})


@login_required
def task_toggle(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == "POST":
        task.toggle()
        if task.is_completed:
            ActivityLog.log(
                request.user,
                ActivityLog.Action.COMPLETED,
                "task",
                f'Completed task "{task.title}"',
                task.pk,
            )
        else:
            ActivityLog.log(
                request.user,
                ActivityLog.Action.REOPENED,
                "task",
                f'Reopened task "{task.title}"',
                task.pk,
            )
        messages.success(request, "Task status updated.")
    return redirect(request.META.get("HTTP_REFERER", "planner:task_list"))


# --- Task categories ------------------------------------------------------
@login_required
def category_list(request):
    categories = TaskCategory.objects.filter(user=request.user)
    if request.method == "POST":
        form = TaskCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, "Category added.")
            return redirect("planner:category_list")
    else:
        form = TaskCategoryForm()
    return render(
        request,
        "planner/category_list.html",
        {"categories": categories, "form": form},
    )


@login_required
def category_delete(request, pk):
    category = get_object_or_404(TaskCategory, pk=pk, user=request.user)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted.")
    return redirect("planner:category_list")
