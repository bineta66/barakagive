from rest_framework.permissions import BasePermission

from apps.common.permissions import IsFinanceModuleRole
from apps.common.scoping import object_belongs_to_user_org

# Accès au module Finance
FINANCE_ROLES = {
    "SUPER_ADMIN",
    "GERANT",
    "CHEF_PROJET",
    "FINANCE",
}

# Création / modification
WRITE_ROLES = {
    "GERANT",
    "SUPER_ADMIN",
    "FINANCE",
}


class FinancePermission(IsFinanceModuleRole):
    """Isolation + rôles du module finance (plus d'accès AGENT ni lecture globale)."""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if request.method in {"GET", "HEAD", "OPTIONS"}:
            return True
        # Analysis/chat POSTs do not mutate financial records.
        if view.__class__.__name__ in {"BudgetAnalysisView", "FinanceAssistantChatView"}:
            return True
        return request.user.role in WRITE_ROLES

    def has_object_permission(self, request, view, obj):
        return object_belongs_to_user_org(obj, request.user)


class CanApproveExpense(BasePermission):
    """
    Seul le Chef de Projet ou le Gérant peut approuver une dépense.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ["FINANCE", "SUPER_ADMIN"]
        )
