"""AI chat assistant models: Conversation and Message."""

from django.conf import settings
from django.db import models
from django.urls import reverse


class Conversation(models.Model):
    """A chat conversation between a user and the AI assistant.

    Maps to the ``ai_conversation`` table (User -> Many Conversations).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    title = models.CharField(max_length=200, default="New conversation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    def get_absolute_url(self):
        return reverse("ai_assistant:conversation", args=[self.pk])

    @property
    def message_count(self):
        return self.messages.count()

    @property
    def preview(self):
        first = self.messages.filter(sender=Message.Sender.USER).first()
        return first.message[:60] if first else "No messages yet"


class Message(models.Model):
    """A single message within a conversation.

    Maps to the ``ai_message`` table (Conversation -> Many Messages).
    """

    class Sender(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.CharField(max_length=10, choices=Sender.choices)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender}: {self.message[:40]}"

    @property
    def is_user(self):
        return self.sender == self.Sender.USER
