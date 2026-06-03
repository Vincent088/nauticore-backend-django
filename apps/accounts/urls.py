from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # auth
    path("register/", views.RegisterView.as_view(), name="auth-register"),
    path("login/", views.LoginView.as_view(), name="auth-login"),
    path("logout/", views.LogoutView.as_view(), name="auth-logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="auth-token-refresh"),
    # current user
    path("me/detail/", views.MeDetailView.as_view(), name="auth-me-detail"),
    path("me/update/", views.MeUpdateView.as_view(), name="auth-me-update"),
    path(
        "me/profile/update/",
        views.UpdateProfileView.as_view(),
        name="auth-profile-update",
    ),
    path(
        "me/password/change/",
        views.ChangePasswordView.as_view(),
        name="auth-password-change",
    ),
    # users
    path("users/list/", views.UserListView.as_view(), name="auth-users-list"),
]
