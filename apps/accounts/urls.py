"""
URL patterns for the accounts app.
Mounted at: /api/v1/auth/

Full JWT auth flow:
  POST  register/           — sign up
  POST  login/              — sign in → get access + refresh tokens
  POST  token/refresh/      — get new access token using refresh token
  POST  token/verify/       — check if an access token is valid
  POST  logout/             — invalidate refresh token
  GET   me/                 — get current user (lightweight, no extra DB query)
  GET   profile/            — full profile
  PATCH profile/            — update profile
  PATCH avatar/             — upload / replace avatar image
  POST  change-password/    — change password
"""

from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    TokenRefreshView,
    TokenVerifyView,
    LogoutView,
    MeView,
    ProfileView,
    AvatarUploadView,
    ChangePasswordView,
)

app_name = "accounts"

urlpatterns = [
    # Public auth endpoints
    path("register/",        RegisterView.as_view(),       name="register"),
    path("login/",           LoginView.as_view(),          name="login"),
    path("token/refresh/",   TokenRefreshView.as_view(),   name="token_refresh"),
    path("token/verify/",    TokenVerifyView.as_view(),    name="token_verify"),
    path("logout/",          LogoutView.as_view(),         name="logout"),

    # Protected user endpoints
    path("me/",              MeView.as_view(),             name="me"),
    path("profile/",         ProfileView.as_view(),        name="profile"),
    path("avatar/",          AvatarUploadView.as_view(),   name="avatar"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
]
