from django.contrib import admin

from .models import EmailVerification, PasswordResetToken, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "phone", "location", "created_at")
    search_fields = ("user__username", "user__email", "full_name", "phone")
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ("user", "is_verified", "created_at", "expires_at")
    list_filter = ("is_verified", "created_at")
    search_fields = ("user__username", "user__email", "token")
    readonly_fields = ("token", "created_at")


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "is_used", "created_at", "expires_at")
    list_filter = ("is_used", "created_at")
    search_fields = ("user__username", "user__email", "token")
    readonly_fields = ("token", "created_at")
