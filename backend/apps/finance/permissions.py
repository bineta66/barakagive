from rest_framework.permissions import BasePermission


READ_ROLES = {"SUPER_ADMIN", "GERANT", "CHEF_PROJET", "FINANCE"}
WRITE_ROLES = {"SUPER_ADMIN", "FINANCE"}


class FinancePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or user.role not in READ_ROLES:
            return False
        if request.method in {"GET", "HEAD", "OPTIONS"}:
            return True
        return user.role in WRITE_ROLES


class SuperAdminPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "SUPER_ADMIN"


class OrganizationManagerPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if request.method in {"GET", "HEAD", "OPTIONS"}:
            return user.role in READ_ROLES
        if request.method == "DELETE":
            return user.role == "SUPER_ADMIN"
        return user.role in {"SUPER_ADMIN", "GERANT"}


class JustificatifPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or user.role not in READ_ROLES:
            return False
        if request.method in {"GET", "HEAD", "OPTIONS"}:
            return True
        return user.role in WRITE_ROLES