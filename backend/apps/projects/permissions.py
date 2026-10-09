from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.common.scoping import is_super_admin, object_belongs_to_user_org


class IsGerantOrFinanceOrAgent(BasePermission):
    """
    Accès pour GERANT, CHEF_PROJET, RESPONSABLE_FINANCE et AGENT.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ["SUPER_ADMIN", "GERANT", "CHEF_PROJET", "FINANCE", "AGENT"]
        )


class CanManageProject(BasePermission):
    """
    GERANT peut créer, modifier, archiver les projets de son ONG.
    CHEF_PROJET peut seulement consulter les projets qui lui sont assignés.
    RESPONSABLE_FINANCE peut uniquement modifier le budget.
    AGENT a accès en lecture seule.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        action = getattr(view, "action", None)
        method = request.method

        if request.user.role == "SUPER_ADMIN":
            return method in SAFE_METHODS

        if request.user.role == "AGENT":
            return method in ["GET", "HEAD", "OPTIONS"] or action in ["list", "retrieve"]
        if request.user.role == "FINANCE":
            return method in ["GET", "HEAD", "OPTIONS", "PATCH"] or action in ["list", "retrieve", "update_budget"]
        if request.user.role == "GERANT":
            return True
        if request.user.role == "CHEF_PROJET":
            return method in ["GET", "HEAD", "OPTIONS"]
        return False

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if not object_belongs_to_user_org(obj, request.user):
            return False
        action = getattr(view, "action", None)
        method = request.method

        if is_super_admin(request.user):
            return True
        if request.user.role == "AGENT":
            return method in SAFE_METHODS or action in ["retrieve"]
        if request.user.role == "FINANCE":
            if action == "update_budget" or "budget" in request.path:
                return True
            return method in SAFE_METHODS or action in ["list", "retrieve"]
        if request.user.role == "GERANT":
            return True
        if request.user.role == "CHEF_PROJET":
            return method in SAFE_METHODS and obj.chef_projet == request.user
        return False


class CanManageProjectCriteria(BasePermission):
    """Only a gérant or the assigned project lead may change project criteria."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in ["SUPER_ADMIN", "GERANT", "CHEF_PROJET"]

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.role == "SUPER_ADMIN":
            return True
        if request.user.role == "GERANT":
            return True
        if request.user.role == "CHEF_PROJET":
            return obj.projet.chef_projet == request.user
        return False
