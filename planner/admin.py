from django.contrib import admin

from .models import Task, TaskCategory


@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "created_at")
    search_fields = ("name", "user__username")
    list_filter = ("created_at",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "priority",
        "status",
        "due_date",
        "is_completed",
        "created_at",
    )
    list_filter = ("priority", "status", "is_completed", "due_date")
    search_fields = ("title", "description", "user__username")
    filter_horizontal = ("categories",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
