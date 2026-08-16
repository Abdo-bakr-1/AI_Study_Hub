"""URL routes for authentication and account management."""

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("verify-email/<str:token>/", views.verify_email, name="verify_email"),
    path("resend-verification/", views.resend_verification, name="resend_verification"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("profile/password/", views.change_password, name="change_password"),
    path(
        "password-reset/",
        views.password_reset_request,
        name="password_reset_request",
    ),
    path(
        "password-reset/<str:token>/",
        views.password_reset_confirm,
        name="password_reset_confirm",
    ),
]
