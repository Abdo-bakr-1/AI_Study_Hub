"""Core views: landing page and error handlers."""

from django.shortcuts import redirect, render


def home(request):
    """Public landing page. Authenticated users go straight to the dashboard."""
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    return render(request, "core/home.html")


# --- Error handlers -------------------------------------------------------
def error_404(request, exception=None):
    return render(request, "errors/404.html", status=404)


def error_403(request, exception=None):
    return render(request, "errors/403.html", status=403)


def error_500(request):
    return render(request, "errors/500.html", status=500)
