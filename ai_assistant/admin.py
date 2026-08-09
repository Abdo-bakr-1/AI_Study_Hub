from django.contrib import admin

from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("sender", "message", "created_at")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "message_count", "created_at", "updated_at")
    search_fields = ("title", "user__username")
    list_filter = ("created_at",)
    inlines = [MessageInline]
    readonly_fields = ("created_at", "updated_at")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "sender", "short_message", "created_at")
    list_filter = ("sender", "created_at")
    search_fields = ("message", "conversation__title")
    readonly_fields = ("created_at",)

    @admin.display(description="Message")
    def short_message(self, obj):
        return obj.message[:60]
