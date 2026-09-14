from rest_framework.permissions import BasePermission


class IsGerantOrFinanceOrAgent(BasePermission):
    """
    Accès pour GERANT, RESPONSABLE_FINANCE et AGENT.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ["GERANT", "FINANCE", "AGENT"]
        )


class CanManageProject(BasePermission):
    """
    GERANT peut créer, modifier, archiver les projets de son ONG.
    RESPONSABLE_FINANCE peut uniquement modifier le budget.
    AGENT a accès en lecture seule.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role == "AGENT":
            return view.action in ["list", "retrieve"]
        if request.user.role == "FINANCE":
            return view.action in ["list", "retrieve", "update_budget"]
        if request.user.role == "GERANT":
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.role == "AGENT":
            return view.action in ["retrieve"]
        if request.user.role == "FINANCE":
            if view.action == "update_budget":
                return True
            return view.action in ["list", "retrieve"]
        if request.user.role == "GERANT":
            if view.action in ["update", "destroy"]:
                return obj.organization == request.user.organization
            return True
        return False
