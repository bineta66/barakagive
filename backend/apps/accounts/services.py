import secrets
import string
import uuid

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.organizations.models import Organization, Subscription
from .models import User, ActivationToken
from .tasks import send_invitation_email

TOKEN_EXPIRY_DAYS = 1


def create_activation_token(user):
    """
    Crée un token UUID unique pour l'activation.
    """
    return ActivationToken.objects.create(
        user=user,
        expires_at=timezone.now() + timezone.timedelta(days=TOKEN_EXPIRY_DAYS),
    )


def send_activation_email(user, activation_token, subject_override=None, html_override=None):
    """
    Envoie l'email contenant le UUID du token.
    """
    activation_link = (
        f"{settings.FRONTEND_URL}/activation/{activation_token.id}"
    )

    send_invitation_email.delay(
        recipient_email=user.email,
        first_name=user.first_name,
        activation_link=activation_link,
        temporary_password=getattr(user, "_temporary_password", None),
        subject_override=subject_override,
        html_override=html_override,
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

    temporary_password = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    gerant = User.objects.create_user(
        email=manager_email,
        first_name=manager_first_name,
        last_name=manager_last_name,
        phone=manager_phone,
        role=User.Role.GERANT,
        organization=organization,
        password=temporary_password,
    )

    gerant.status = User.Status.EN_ATTENTE
    gerant.is_active = False
    gerant.must_change_password = True
    gerant.last_invited_at = timezone.now()
    gerant.save()
    gerant._temporary_password = temporary_password

    activation = create_activation_token(gerant)
    send_activation_email(gerant, activation)

    return gerant


@transaction.atomic
def register_organization_and_gerant(data):
    organization = Organization.objects.create(
        name=data["organization_name"],
        acronym=data.get("organization_acronym", ""),
        email=data["organization_email"],
        phone=data["organization_phone"],
        country=data.get("country", "Sénégal"),
        region=data["region"],
        address=data["address"],
        description=data.get("organization_description", ""),
        logo=data.get("logo"),
        status=Organization.Status.EN_ATTENTE,
        is_active=False,
    )
    user = create_gerant_for_organization(
        organization=organization,
        manager_first_name=data["first_name"],
        manager_last_name=data["last_name"],
        manager_email=data["email"],
        manager_phone=data["phone"],
    )
    return organization, user


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
    user.must_change_password = True
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
        clean_token = str(token).strip().strip('"').strip("'")
        token_uuid = uuid.UUID(clean_token)
    except (ValueError, TypeError):
        raise ValidationError(
            {"detail": "Le lien d'activation est invalide."}
        )

    # Rechercher le token
    try:
        activation = ActivationToken.objects.select_related("user", "user__organization").get(
            id=token_uuid
        )
    except ActivationToken.DoesNotExist:
        raise ValidationError(
            {"detail": "Le lien d'activation est introuvable ou n'existe plus."}
        )

    user = activation.user

    if user.status == User.Status.SUSPENDED:
        raise ValidationError({"detail": "Ce compte est suspendu. Contactez votre administrateur."})
    if user.organization and user.organization.status == Organization.Status.SUSPENDED:
        raise ValidationError({"detail": "Cette organisation est suspendue."})

    # Déjà utilisé : si l'utilisateur a déjà un mot de passe et est actif, l'inviter à se connecter
    if activation.used:
        if user.has_usable_password() and user.is_active and not user.must_change_password:
            raise ValidationError(
                {"detail": "Ce compte est déjà activé. Vous pouvez vous connecter directement."}
            )

    # Expiré : tolérance si le compte n'a pas encore été activé
    if activation.expires_at < timezone.now() - timezone.timedelta(days=7):
        raise ValidationError(
            {"detail": "Le lien d'activation est expiré. Veuillez demander un nouvel email d'activation."}
        )

    # Activation du compte
    if password:
        user.set_password(password)
        user.must_change_password = False
    user.status = User.Status.ACTIVE
    user.is_active = True

    if user.organization:
        try:
            user.organization.status = Organization.Status.ACTIVE
            user.organization.is_active = True
            user.organization.save()
        except Exception:
            pass

        try:
            if not Subscription.objects.filter(organization=user.organization).exists():
                Subscription.objects.create(
                    organization=user.organization,
                    status=Subscription.Status.TRIAL,
                    trial_start=timezone.now().date(),
                    trial_end=timezone.now().date() + timezone.timedelta(days=30),
                )
        except Exception:
            pass

    user.save()

    try:
        activation.used = True
        activation.save(update_fields=["used"])
    except Exception:
        activation.save()

    return user


@transaction.atomic
def change_password(user, current_password, new_password):
    if not user.check_password(current_password):
        raise ValidationError({"current_password": "Le mot de passe actuel est incorrect."})
    user.set_password(new_password)
    user.must_change_password = False
    user.save(update_fields=["password", "must_change_password"])
    return user


@transaction.atomic
def resend_activation(email):
    try:
        user = User.objects.select_related("organization").get(email=email)
    except User.DoesNotExist:
        raise ValidationError({"detail": "Aucun compte ne correspond à cet email."})
    if user.status == User.Status.SUSPENDED:
        raise ValidationError({"detail": "Ce compte est suspendu."})
    if user.is_active:
        raise ValidationError({"detail": "Ce compte est déjà actif."})
    ActivationToken.objects.filter(user=user, used=False).update(used=True)
    token = create_activation_token(user)
    send_activation_email(user, token)
    return token
