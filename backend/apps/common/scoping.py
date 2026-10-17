"""Isolation des données par organisation (ONG)."""

from rest_framework.exceptions import ValidationError

from apps.accounts.models import User


def is_super_admin(user):
    return bool(user and getattr(user, "role", None) == User.Role.SUPER_ADMIN)


def user_organization(user):
    return getattr(user, "organization", None) if user else None


def scope_by_organization(queryset, user, lookup="organization"):
    """
    Restreint un QuerySet à l'ONG de l'utilisateur.
    Le Super Admin conserve une vue globale.
    Un utilisateur sans ONG ne voit rien.
    """
    if user is None or not getattr(user, "is_authenticated", False):
        return queryset.none()
    if is_super_admin(user):
        return queryset
    organization = user_organization(user)
    if organization is None:
        return queryset.none()
    return queryset.filter(**{lookup: organization})


def object_belongs_to_user_org(obj, user):
    if obj is None or user is None:
        return False
    if is_super_admin(user):
        return True
    organization = user_organization(user)
    if organization is None:
        return False

    obj_org = getattr(obj, "organization", None)
    if obj_org is None and hasattr(obj, "depense"):
        obj_org = getattr(obj.depense, "organization", None)
    if obj_org is None and hasattr(obj, "projet"):
        obj_org = getattr(obj.projet, "organization", None)
    if obj_org is None and hasattr(obj, "formulaire"):
        obj_org = getattr(obj.formulaire, "organization", None)
    return obj_org == organization


def reject_foreign_organization_payload(data, user):
    """
    Refuse un organization / organization_id différent de l'ONG du compte.
    L'organisation métier est toujours celle de l'utilisateur authentifié.
    """
    if user is None or is_super_admin(user):
        return
    raw_id = None
    if hasattr(data, "get"):
        raw_id = data.get("organization_id")
        if raw_id in (None, ""):
            raw_id = data.get("organization")
    if raw_id in (None, ""):
        return
    if hasattr(raw_id, "pk"):
        raw_id = raw_id.pk
    try:
        injected = int(raw_id)
    except (TypeError, ValueError):
        raise ValidationError({
            "organization": "Identifiant d'organisation invalide.",
        })
    expected = getattr(user, "organization_id", None)
    if expected is None or injected != int(expected):
        raise ValidationError({
            "organization": (
                "L'organisation est déterminée par votre compte "
                "et ne peut pas être imposée."
            ),
        })
