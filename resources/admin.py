from django.contrib import admin

from .models import Resource, ResourceCategory


@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "created_at")
    search_fields = ("name", "user__username")
    list_filter = ("created_at",)


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "resource_type", "link", "created_at")
    list_filter = ("resource_type", "created_at", "categories")
    search_fields = ("title", "description", "link", "user__username")
    filter_horizontal = ("categories",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
