"""AI service layer.

This module isolates all communication with the AI provider so views never
talk to the provider directly. It targets any OpenAI-compatible Chat
Completions endpoint (Google Gemini, OpenAI, Groq, OpenRouter, local
servers, ...), which is configured entirely through environment variables
(see ``config/settings.py``).

If no API key is configured the service returns a helpful offline fallback
response so the application remains fully runnable during development and
grading without leaking or requiring secrets.
"""

from __future__ import annotations

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are the AI Study Assistant inside 'AI Study Hub', a study-management "
    "web app. You help students by explaining programming concepts, clarifying "
    "errors, answering study questions, creating study plans, summarizing study "
    "content, and generating practice questions or flashcards. Be clear, "
    "concise and encouraging. Use short paragraphs and lists when helpful. If a "
    "question needs the student's personal data that was not provided, say so "
    "instead of inventing details."
)


class AIServiceError(Exception):
    """Raised when the AI provider request fails."""


def is_configured() -> bool:
    """Return True when an API key is available."""
    return bool(settings.AI_API_KEY)


def build_messages(history, new_message, extra_context=""):
    """Assemble the message list sent to the provider.

    ``history`` is an iterable of (role, content) tuples in chronological
    order. ``extra_context`` is optional structured data (e.g. the user's own
    tasks) that Django has already fetched.
    """
    system_content = SYSTEM_PROMPT
    if extra_context:
        system_content += (
            "\n\nHere is relevant context about the current user that you may "
            "use to answer. Only use it if relevant:\n" + extra_context
        )

    messages = [{"role": "system", "content": system_content}]
    for role, content in history:
        # Map our stored 'assistant'/'user' roles straight through.
        messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": new_message})
    return messages


def get_ai_response(history, new_message, extra_context=""):
    """Return the assistant's reply text for ``new_message``.

    Falls back to an offline canned response when no key is configured.
    Raises ``AIServiceError`` on a genuine provider/network failure.
    """
    if not is_configured():
        return _offline_response(new_message)

    messages = build_messages(history, new_message, extra_context)
    url = settings.AI_API_BASE_URL.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.AI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.AI_MODEL,
        "messages": messages,
        "max_tokens": settings.AI_MAX_TOKENS,
        "temperature": 0.7,
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=settings.AI_REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout as exc:
        logger.error("AI request timed out: %s", exc)
        raise AIServiceError(
            "The AI provider took too long to respond. Please try again."
        ) from exc
    except requests.exceptions.RequestException as exc:
        logger.error("AI request failed: %s", exc)
        raise AIServiceError(
            "Sorry, the AI assistant is temporarily unavailable. "
            "Please try again in a moment."
        ) from exc

    try:
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, ValueError) as exc:
        logger.error("Unexpected AI response format: %s", exc)
        raise AIServiceError(
            "Received an unexpected response from the AI provider."
        ) from exc


def _offline_response(message: str) -> str:
    """A deterministic, helpful response used when no API key is set."""
    trimmed = message.strip()
    preview = (trimmed[:180] + "...") if len(trimmed) > 180 else trimmed
    return (
        "AI provider is not configured yet, so I'm replying in offline demo "
        "mode.\n\n"
        f'You asked: "{preview}"\n\n'
        "To enable real AI answers, set the AI_API_KEY environment variable in "
        "your .env file (see .env.example) and restart the server. Meanwhile I "
        "can still store your conversation history so you can test the chat "
        "interface end to end."
    )
