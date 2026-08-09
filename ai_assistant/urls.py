"""URL routes for the AI chat assistant."""

from django.urls import path

from . import views

app_name = "ai_assistant"

urlpatterns = [
    path("", views.chat, name="chat"),
    path("new/", views.new_conversation, name="new"),
    path("send/", views.send_message, name="send_new"),
    path("<int:pk>/", views.conversation_detail, name="conversation"),
    path("<int:pk>/send/", views.send_message, name="send"),
    path("<int:pk>/clear/", views.clear_conversation, name="clear"),
    path("<int:pk>/delete/", views.delete_conversation, name="delete"),
]
