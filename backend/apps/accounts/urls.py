from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .jwt_views import JWTLoginView, LogoutView
from .views import (
    ActivateAccountView,
    UserListView,
    UserCreateView,
)

app_name = "accounts"

urlpatterns = [
    # Authentification
    path("login/", JWTLoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),

    # Activation du compte
    path("activate/", ActivateAccountView.as_view(), name="activate"),

    # Gestion des utilisateurs
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/create/", UserCreateView.as_view(), name="user-create"),
]