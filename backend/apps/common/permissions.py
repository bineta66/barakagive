from rest_framework.permissions import BasePermission

from apps.accounts.models import User
from .scoping import is_super_admin, object_belongs_to_user_org, user_organization


class BelongsToUserOrganization(BasePermission):
    """Refuse l'accès objet si la ressource n'appartient pas à l'ONG de l'utilisateur."""

    message = "Cette ressource n'appartient pas à votre organisation."

    def has_object_permission(self, request, view, obj):
        return object_belongs_to_user_org(obj, request.user)


class HasOrganization(BasePermission):
    """Exige une organisation, sauf pour le Super Admin."""

    message = "Aucune organisation n'est associée à ce compte."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if is_super_admin(user):
            return True
        return user_organization(user) is not None


class IsFinanceModuleRole(BasePermission):
    """Lecture / écriture finance : GERANT, CHEF_PROJET, FINANCE (et Super Admin)."""

    message = "Accès au module finance non autorisé pour ce rôle."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if not user.can_login:
            return False
        if is_super_admin(user):
            return True
        if user.role not in {User.Role.GERANT, User.Role.CHEF_PROJET, User.Role.FINANCE}:
            return False
        return user_organization(user) is not None

    def has_object_permission(self, request, view, obj):
        return object_belongs_to_user_org(obj, request.user)
