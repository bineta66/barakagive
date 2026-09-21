from rest_framework.permissions import BasePermission

FINANCE_ROLES = {"SUPER_ADMIN", "GERANT", "FINANCE"}
WRITE_ROLES = {"SUPER_ADMIN", "GERANT", "FINANCE"}


class FinancePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or user.role not in FINANCE_ROLES:
            return False
        if request.method in {"GET", "HEAD", "OPTIONS"}:
            return True
        return user.role in WRITE_ROLES