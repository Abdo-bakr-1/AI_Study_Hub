"""Views for the AI chat assistant.

The chat page works both as a normal Django form submission (progressive
enhancement) and via a fetch/AJAX request that returns JSON. No DRF is used —
just plain Django views returning ``JsonResponse``.
"""

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .context import build_user_context
from .forms import MessageForm
from .models import Conversation, Message
from .services import AIServiceError, get_ai_response

HISTORY_LIMIT = 20  # how many previous messages to send as context


def _user_conversations(user):
    return Conversation.objects.filter(user=user)


@login_required
def chat(request):
    """Show the most recent conversation (or an empty state)."""
    conversation = _user_conversations(request.user).first()
    if conversation:
        return redirect("ai_assistant:conversation", pk=conversation.pk)
    return render(
        request,
        "ai_assistant/chat.html",
        {
            "conversation": None,
            "conversations": _user_conversations(request.user),
            "chat_messages": [],
            "form": MessageForm(),
        },
    )


@login_required
def conversation_detail(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk, user=request.user)
    return render(
        request,
        "ai_assistant/chat.html",
        {
            "conversation": conversation,
            "conversations": _user_conversations(request.user),
            "chat_messages": conversation.messages.all(),
            "form": MessageForm(),
        },
    )


@login_required
@require_POST
def new_conversation(request):
    conversation = Conversation.objects.create(user=request.user)
    return redirect("ai_assistant:conversation", pk=conversation.pk)


@login_required
@require_POST
def send_message(request, pk=None):
    """Handle a chat message. Returns JSON for AJAX, redirects otherwise."""
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    # Get or create the conversation (scoped to the user).
    if pk:
        conversation = get_object_or_404(Conversation, pk=pk, user=request.user)
    else:
        conversation = Conversation.objects.create(user=request.user)

    form = MessageForm(request.POST)
    if not form.is_valid():
        error = "Please enter a message."
        if is_ajax:
            return JsonResponse({"success": False, "error": error}, status=400)
        messages.error(request, error)
        return redirect("ai_assistant:conversation", pk=conversation.pk)

    user_text = form.cleaned_data["message"]

    # Persist the user message.
    user_message = Message.objects.create(
        conversation=conversation,
        sender=Message.Sender.USER,
        message=user_text,
    )

    # Give the conversation a title from the first message.
    if conversation.title == "New conversation" or not conversation.title:
        conversation.title = user_text[:60]
        conversation.save(update_fields=["title", "updated_at"])
    else:
        conversation.save(update_fields=["updated_at"])

    # Build recent history for the provider (everything except the message
    # just persisted, so repeated text isn't dropped from context).
    history_qs = conversation.messages.exclude(pk=user_message.pk).order_by(
        "created_at"
    )[:HISTORY_LIMIT]
    history = [(m.sender, m.message) for m in history_qs]

    extra_context = build_user_context(request.user)

    try:
        reply = get_ai_response(history, user_text, extra_context)
    except AIServiceError as exc:
        error_text = str(exc)
        if is_ajax:
            return JsonResponse(
                {"success": False, "error": error_text}, status=502
            )
        messages.error(request, error_text)
        return redirect("ai_assistant:conversation", pk=conversation.pk)

    ai_message = Message.objects.create(
        conversation=conversation,
        sender=Message.Sender.ASSISTANT,
        message=reply,
    )

    if is_ajax:
        return JsonResponse(
            {
                "success": True,
                "conversation_id": conversation.pk,
                "reply": reply,
                "created_at": ai_message.created_at.strftime("%H:%M"),
                "title": conversation.title,
            }
        )
    return redirect("ai_assistant:conversation", pk=conversation.pk)


@login_required
@require_POST
def clear_conversation(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk, user=request.user)
    conversation.messages.all().delete()
    conversation.title = "New conversation"
    conversation.save(update_fields=["title", "updated_at"])
    messages.info(request, "Conversation cleared.")
    return redirect("ai_assistant:conversation", pk=conversation.pk)


@login_required
@require_POST
def delete_conversation(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk, user=request.user)
    conversation.delete()
    messages.success(request, "Conversation deleted.")
    return redirect("ai_assistant:chat")
