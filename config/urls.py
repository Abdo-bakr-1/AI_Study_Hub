"""Root URL configuration for the AI Study Hub project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("", include("accounts.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("tasks/", include("planner.urls")),
    path("notes/", include("notes.urls")),
    path("resources/", include("resources.urls")),
    path("ai-chat/", include("ai_assistant.urls")),
]

# Serve uploaded media files in development.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# Custom error handlers.
handler404 = "core.views.error_404"
handler403 = "core.views.error_403"
handler500 = "core.views.error_500"
