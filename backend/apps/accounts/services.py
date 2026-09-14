import uuid
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.organizations.models import Organization
from .models import User, ActivationToken
from .tasks import send_invitation_email

TOKEN_EXPIRY_DAYS = 7


def create_activation_token(user):
    """
    Crée un token UUID unique pour l'activation.
    """
    return ActivationToken.objects.create(
        user=user,
        expires_at=timezone.now() + timedelta(days=TOKEN_EXPIRY_DAYS),
    )


def send_activation_email(user, activation_token):
    """
    Envoie l'email contenant le UUID du token.
    """
    activation_link = (
        f"http://localhost:5173/activate?token={activation_token.id}"
    )

    send_invitation_email.delay(
        recipient_email=user.email,
        first_name=user.first_name,
        activation_link=activation_link,
    )


@transaction.atomic
def create_gerant_for_organization(
    *,
    organization: Organization,
    manager_first_name: str,
    manager_last_name: str,
    manager_email: str,
    manager_phone: str,
):
    """
    Création automatique du gérant après l'inscription d'une ONG.
    """

    gerant = User.objects.create_user(
        email=manager_email,
        first_name=manager_first_name,
        last_name=manager_last_name,
        phone=manager_phone,
        role=User.Role.GERANT,
        organization=organization,
    )

    gerant.status = User.Status.INVITED
    gerant.is_active = False
    gerant.last_invited_at = timezone.now()
    gerant.save()

    activation = create_activation_token(gerant)
    send_activation_email(gerant, activation)

    return gerant


@transaction.atomic
def create_user_by_manager(
    *,
    organization,
    first_name,
    last_name,
    email,
    phone,
    role,
):
    """
    Création d'un Chef de projet, Finance ou Agent.
    """

    user = User.objects.create_user(
        email=email,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        role=role,
        organization=organization,
    )

    user.status = User.Status.INVITED
    user.is_active = False
    user.last_invited_at = timezone.now()
    user.save()

    activation = create_activation_token(user)
    send_activation_email(user, activation)

    return user


@transaction.atomic
def activate_account(token, password):
    """
    Activation d'un compte à partir d'un UUID.
    """

    # Vérifier que le token est un UUID valide
    try:
        token_uuid = uuid.UUID(str(token))
    except ValueError:
        raise ValidationError(
            {"detail": "Le lien d'activation est invalide."}
        )

    # Rechercher le token
    try:
        activation = ActivationToken.objects.select_related("user").get(
            id=token_uuid
        )
    except ActivationToken.DoesNotExist:
        raise ValidationError(
            {"detail": "Le lien d'activation est invalide."}
        )

    # Déjà utilisé
    if activation.used:
        raise ValidationError(
            {"detail": "Ce lien d'activation a déjà été utilisé."}
        )

    # Expiré
    if activation.expires_at < timezone.now():
        raise ValidationError(
            {"detail": "Le lien d'activation est expiré."}
        )

    # Activation du compte
    user = activation.user
    user.set_password(password)
    user.status = User.Status.ACTIVE
    user.is_active = True
    user.save()

    activation.used = True
    activation.save(update_fields=["used"])

    return user