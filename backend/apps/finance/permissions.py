from rest_framework.permissions import BasePermission

# Accès au module Finance
FINANCE_ROLES = {
    "SUPER_ADMIN",
    "GERANT",
    "CHEF_PROJET",
    "FINANCE",
}

# Création / modification
WRITE_ROLES = {
    "SUPER_ADMIN",
    "GERANT",
    "FINANCE",
}


class FinancePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.role not in FINANCE_ROLES:
            return False

        # Lecture autorisée
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        # Écriture : Finance + Gérant
        return user.role in WRITE_ROLES


class CanApproveExpense(BasePermission):
    """
    Seul le Chef de Projet ou le Gérant peut approuver une dépense.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ["CHEF_PROJET", "GERANT"]
        )