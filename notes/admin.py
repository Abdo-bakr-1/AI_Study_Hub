from django.contrib import admin

from .models import Note, NoteCategory


@admin.register(NoteCategory)
class NoteCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "created_at")
    search_fields = ("name", "user__username")
    list_filter = ("created_at",)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created_at", "updated_at")
    list_filter = ("created_at", "categories")
    search_fields = ("title", "content", "user__username")
    filter_horizontal = ("categories",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
