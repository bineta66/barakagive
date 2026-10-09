from django.urls import path
from .jwt_views import ActiveTokenRefreshView, JWTLoginView, LogoutView
from .views import (
    ActivateAccountView,
    AgentListView,
    UserListView,
    UserCreateView,
    UserDetailView,
    MeView,
    RegisterAuthView,
    ChangePasswordView,
    ResendActivationView,
    GerantListView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    InAppNotificationListView,
    InAppNotificationReadView,
)

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterAuthView.as_view(), name="auth-register"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("resend-activation/", ResendActivationView.as_view(), name="resend-activation"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path("password-reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    # Authentification
    path("login/", JWTLoginView.as_view(), name="login"),
    path("refresh/", ActiveTokenRefreshView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),

    # Activation du compte
    path("activate/", ActivateAccountView.as_view(), name="activate"),

    # Gestion des utilisateurs
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("users/create/", UserCreateView.as_view(), name="user-create"),
    path("agents/", AgentListView.as_view(), name="agent-list"),
    path("gerants/", GerantListView.as_view(), name="gerant-list"),
    path("me/", MeView.as_view(), name="me"),
    path("notifications/", InAppNotificationListView.as_view(), name="notification-list"),
    path("notifications/<uuid:notification_id>/read/", InAppNotificationReadView.as_view(), name="notification-read"),
]
