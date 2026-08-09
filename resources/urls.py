"""URL routes for the learning resources app."""

from django.urls import path

from . import views

app_name = "resources"

urlpatterns = [
    path("", views.resource_list, name="list"),
    path("add/", views.resource_create, name="create"),
    path("categories/", views.category_list, name="category_list"),
    path(
        "categories/<int:pk>/delete/",
        views.category_delete,
        name="category_delete",
    ),
    path("<int:pk>/", views.resource_detail, name="detail"),
    path("<int:pk>/edit/", views.resource_edit, name="edit"),
    path("<int:pk>/delete/", views.resource_delete, name="delete"),
]
