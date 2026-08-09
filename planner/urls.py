"""URL routes for the study planner."""

from django.urls import path

from . import views

app_name = "planner"

urlpatterns = [
    path("", views.task_list, name="task_list"),
    path("add/", views.task_create, name="task_create"),
    path("categories/", views.category_list, name="category_list"),
    path(
        "categories/<int:pk>/delete/",
        views.category_delete,
        name="category_delete",
    ),
    path("<int:pk>/", views.task_detail, name="task_detail"),
    path("<int:pk>/edit/", views.task_edit, name="task_edit"),
    path("<int:pk>/delete/", views.task_delete, name="task_delete"),
    path("<int:pk>/toggle/", views.task_toggle, name="task_toggle"),
]
