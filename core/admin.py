from django.contrib import admin

from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "content_type", "description", "created_at")
    list_filter = ("action", "content_type", "created_at")
    search_fields = ("user__username", "description")
    readonly_fields = ("created_at",)
