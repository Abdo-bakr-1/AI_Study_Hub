"""URL routes for the notes app."""

from django.urls import path

from . import views

app_name = "notes"

urlpatterns = [
    path("", views.note_list, name="list"),
    path("add/", views.note_create, name="create"),
    path("export/pdf/", views.export_notes_pdf, name="export_pdf"),
    path("categories/", views.category_list, name="category_list"),
    path(
        "categories/<int:pk>/delete/",
        views.category_delete,
        name="category_delete",
    ),
    path("<int:pk>/", views.note_detail, name="detail"),
    path("<int:pk>/edit/", views.note_edit, name="edit"),
    path("<int:pk>/delete/", views.note_delete, name="delete"),
]
