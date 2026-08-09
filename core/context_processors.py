"""Template context processors shared across all pages."""


def site_context(request):
    """Inject site-wide values into every template context."""
    return {
        "SITE_NAME": "AI Study Hub",
        "SITE_TAGLINE": "Organize your study life with an AI assistant",
    }
