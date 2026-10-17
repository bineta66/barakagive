import uuid
import logging
from django.conf import settings
from django.db.models import F, Q
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.core import signing
from rest_framework import generics, status, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.common.pagination import StandardPagination

from drf_spectacular.utils import extend_schema

from .models import User, InAppNotification
from .serializers import (
    UserSerializer,
    CreateUserSerializer,
    ActivateAccountSerializer,
    RegisterAuthSerializer,
    ChangePasswordSerializer,
    ResendActivationSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    AgentListSerializer,
)
from .permissions import IsAccountActive

logger = logging.getLogger(__name__)


class InAppNotificationListView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive]

    def get(self, request):
        notifications = InAppNotification.objects.filter(
            recipient=request.user,
            organization_id=request.user.organization_id,
        ).filter(
            Q(project__isnull=True) | Q(project__organization_id=F("organization_id"))
        ).select_related("project")[:30]
        return Response({
            "unread_count": InAppNotification.objects.filter(
                recipient=request.user,
                organization_id=request.user.organization_id,
                read_at__isnull=True,
            ).filter(
                Q(project__isnull=True) | Q(project__organization_id=F("organization_id"))
            ).count(),
            "results": [{
                "id": str(item.id), "title": item.title, "message": item.message,
                "project": item.project.name if item.project_id else None,
                "source": item.source, "created_at": item.created_at.isoformat(),
                "read": item.read_at is not None,
            } for item in notifications],
        })


class InAppNotificationReadView(APIView):
    permission_classes = [IsAuthenticated, IsAccountActive]

    def post(self, request, notification_id):
        notification = InAppNotification.objects.filter(
            pk=notification_id,
            recipient=request.user,
            organization_id=request.user.organization_id,
        ).filter(
            Q(project__isnull=True) | Q(project__organization_id=F("organization_id"))
        ).first()
        if not notification:
            return Response({"detail": "Notification introuvable."}, status=status.HTTP_404_NOT_FOUND)
        if notification.read_at is None:
            notification.read_at = timezone.now()
            notification.save(update_fields=["read_at"])
        return Response({"id": str(notification.id), "read": True})


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].strip().lower()
        user = User.objects.filter(
            email__iexact=email,
            is_active=True,
            status=User.Status.ACTIVE,
        ).first()
        if user:
            token = signing.dumps(
                {
                    "uid": str(user.pk),
                    "reset_token": default_token_generator.make_token(user),
                },
                salt="barakagive.password-reset",
            )
            link = f"{settings.FRONTEND_URL.rstrip('/')}/reinitialisation?token={token}"
            try:
                from .tasks import send_invitation_email
                send_invitation_email.delay(
                    recipient_email=user.email,
                    first_name=user.first_name or "",
                    activation_link=link,
                    subject_override="Réinitialisation de votre mot de passe BarakaGive360",
                    html_override=(
                        "<p>Une demande de réinitialisation a été effectuée pour votre compte.</p>"
                        f'<p><a href="{link}">Choisir un nouveau mot de passe</a></p>'
                        "<p>Ce lien expire dans une heure. Ignorez ce message si vous n'êtes pas à l'origine de la demande.</p>"
                    ),
                )
            except Exception as exc:
                # Ne pas exposer l'existence du compte ni le contenu du lien dans les logs.
                logger.warning("Password reset email queue failed (%s).", type(exc).__name__)
        return Response({
            "detail": "Si cette adresse correspond à un compte actif, un lien de réinitialisation sera envoyé."
        })


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        user.set_password(serializer.validated_data["password"])
        user.save(update_fields=["password"])
        return Response({"detail": "Votre mot de passe a été réinitialisé."})
from .permissions import (
    IsGerant,
    IsGerantOrChefProjet,
    IsSuperAdmin,
)
from .services import (
    create_user_by_manager,
    activate_account,
    register_organization_and_gerant,
    change_password,
    resend_activation,
)


@extend_schema(tags=["Accounts"], summary="Activer un compte")
class ActivateAccountView(generics.GenericAPIView):
    """
    Activation du compte avec le token reçu.
    """
    serializer_class = ActivateAccountSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        token = request.query_params.get("token")
        if not token:
            return Response({"detail": "Le token est obligatoire."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            import uuid
            clean_token = str(token).strip().strip('"').strip("'")
            token_uuid = uuid.UUID(clean_token)
        except (ValueError, TypeError):
            return Response({"detail": "Le lien d'activation est invalide."}, status=status.HTTP_400_BAD_REQUEST)

        from .models import ActivationToken
        try:
            activation = ActivationToken.objects.select_related("user").get(id=token_uuid)
        except ActivationToken.DoesNotExist:
            return Response({"detail": "Le lien d'activation est introuvable."}, status=status.HTTP_404_NOT_FOUND)

        if activation.used and activation.user.has_usable_password() and not activation.user.must_change_password:
            return Response({"detail": "Ce compte a déjà été activé."}, status=status.HTTP_400_BAD_REQUEST)

        if activation.expires_at < timezone.now() - timezone.timedelta(days=7):
            return Response({"detail": "Ce lien d'activation est expiré."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "valid": True,
            "email": activation.user.email,
            "first_name": activation.user.first_name,
        })

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            errors = serializer.errors
            # Extraire un message d'erreur lisible
            error_msg = "Données d'activation invalides."
            for k, v in errors.items():
                if isinstance(v, list) and len(v) > 0:
                    error_msg = str(v[0])
                    break
                elif isinstance(v, str):
                    error_msg = v
                    break
            return Response({"detail": error_msg, "errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = activate_account(
                token=serializer.validated_data["token"],
                password=serializer.validated_data["password"],
            )
        except ValidationError as e:
            detail = e.detail
            if isinstance(detail, list):
                detail = detail[0]
            elif isinstance(detail, dict):
                detail = next(iter(detail.values()))
                if isinstance(detail, list):
                    detail = detail[0]
            return Response(
                {"detail": str(detail)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {"detail": f"Erreur d'activation : {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Compte activé avec succès.", "email": user.email},
            status=status.HTTP_200_OK,
        )


class RegisterAuthView(generics.GenericAPIView):
    serializer_class = RegisterAuthSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        organization, user = register_organization_and_gerant(serializer.validated_data)
        return Response({
            "message": "Votre inscription a été enregistrée. Consultez votre email pour activer le compte.",
            "organization": {"id": organization.id, "name": organization.name, "status": organization.status},
            "gerant": {"email": user.email, "status": user.status},
        }, status=status.HTTP_201_CREATED)


class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated, IsAccountActive]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = change_password(
            request.user,
            serializer.validated_data["current_password"],
            serializer.validated_data["new_password"],
        )
        return Response({"message": "Mot de passe modifié avec succès.", "user": UserSerializer(user).data})


class ResendActivationView(generics.GenericAPIView):
    serializer_class = ResendActivationSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            resend_activation(serializer.validated_data["email"])
        except ValidationError:
            # Do not reveal whether an account exists, is active, or is suspended.
            pass
        return Response({"message": "Un nouvel email d'activation a été envoyé."})


@extend_schema(tags=["Accounts"], summary="Liste des utilisateurs")
class UserListView(generics.ListAPIView):
    """
    Le Gérant consulte les utilisateurs de son ONG.
    """
    serializer_class = UserSerializer
    permission_classes = [
        IsAuthenticated,
        IsAccountActive,
        IsGerant,
    ]
    pagination_class = StandardPagination

    def get_queryset(self):
        organization = self.request.user.organization
        if organization is None:
            return User.objects.none()
        users = User.objects.filter(organization=organization).order_by("first_name", "pk")
        search = (self.request.query_params.get("search") or "").strip()
        if search:
            users = users.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(phone__icontains=search)
            )
        role = self.request.query_params.get("role")
        if role:
            users = users.filter(role=role)
        account_status = self.request.query_params.get("status")
        if account_status:
            users = users.filter(status=account_status)
        return users


@extend_schema(tags=["Accounts"], summary="Créer un utilisateur")
class UserCreateView(generics.CreateAPIView):
    """
    Le Gérant crée un Chef de projet,
    un Responsable Finance ou un Agent.
    """
    serializer_class = CreateUserSerializer
    permission_classes = [
        IsAuthenticated,
        IsAccountActive,
        IsGerant,
    ]

    def create(self, request, *args, **kwargs):
        if request.user.organization is None:
            return Response(
                {"detail": "Aucune organisation n'est associée à ce compte."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = create_user_by_manager(
            organization=request.user.organization,
            first_name=serializer.validated_data["first_name"],
            last_name=serializer.validated_data["last_name"],
            email=serializer.validated_data["email"],
            phone=serializer.validated_data["phone"],
            role=serializer.validated_data["role"],
        )

        return Response(
            {
                "message": "Invitation envoyée avec succès.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Accounts"], summary="Profil de l'utilisateur connecté")
class MeView(generics.RetrieveAPIView):
    """
    Retourne le profil de l'utilisateur actuellement authentifié.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAccountActive]

    def get_object(self):
        return self.request.user


@extend_schema(tags=["Accounts"], summary="Détail et mise à jour d'un collaborateur (activation/désactivation)")
class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    Le Gérant consulte le détail d'un utilisateur de son ONG
    et peut l'activer ou le désactiver (suspendre).
    """
    serializer_class = UserSerializer
    permission_classes = [
        IsAuthenticated,
        IsAccountActive,
        IsGerant,
    ]

    def get_queryset(self):
        organization = self.request.user.organization
        if organization is None:
            return User.objects.none()
        return User.objects.filter(
            organization=organization
        )

    @staticmethod
    def _reject_sensitive_fields(request):
        protected_fields = {
            "role",
            "organization",
            "organization_id",
            "is_staff",
            "is_superuser",
            "is_super_admin",
            "must_change_password",
            "username",
        }
        attempted = protected_fields.intersection(request.data.keys())
        if attempted:
            return Response(
                {
                    "detail": "Ces champs ne peuvent pas être modifiés via cette API.",
                    "fields": sorted(attempted),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return None

    def update(self, request, *args, **kwargs):
        # Couvre PUT et, via UpdateModelMixin, toute mise à jour générique.
        rejection = self._reject_sensitive_fields(request)
        if rejection:
            return rejection
        return super().update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        rejection = self._reject_sensitive_fields(request)
        if rejection:
            return rejection

        user = self.get_object()
        new_status = request.data.get("status")
        is_active = request.data.get("is_active")

        if new_status or is_active is not None:
            if new_status:
                if new_status not in [User.Status.ACTIVE, User.Status.SUSPENDED, User.Status.INVITED]:
                    return Response(
                        {"detail": "Statut invalide."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                user.status = new_status
                if new_status == User.Status.SUSPENDED:
                    user.is_active = False
                elif new_status == User.Status.ACTIVE:
                    user.is_active = True

            if is_active is not None:
                try:
                    active_value = serializers.BooleanField().run_validation(is_active)
                except serializers.ValidationError:
                    return Response(
                        {"is_active": "La valeur doit être booléenne."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                user.is_active = active_value
                if not user.is_active:
                    user.status = User.Status.SUSPENDED
                elif user.status == User.Status.SUSPENDED:
                    user.status = User.Status.ACTIVE

            user.save()
            return Response(UserSerializer(user).data)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@extend_schema(tags=["Accounts"], summary="Liste des agents terrain de l'ONG")
class AgentListView(generics.ListAPIView):
    """
    Liste les agents terrain (et chefs de projet) de la même ONG,
    pour l'affectation d'une campagne par le gérant ou le chef de projet.
    """

    serializer_class = AgentListSerializer
    permission_classes = [IsAuthenticated, IsAccountActive, IsGerantOrChefProjet]
    pagination_class = StandardPagination

    def get_queryset(self):
        organization_id = self.request.user.organization_id
        if not organization_id:
            return User.objects.none()
        queryset = User.objects.filter(
            organization_id=organization_id,
            role__in=[User.Role.AGENT, User.Role.CHEF_PROJET],
        ).exclude(
            status=User.Status.SUSPENDED
        )
        search = (self.request.query_params.get("search") or "").strip()
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(phone__icontains=search)
            )
        return queryset.order_by("last_name", "first_name", "pk")

# Serializer pour le Super Admin avec infos complètes de l'ONG
class GerantWithOrganizationSerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    status_ong = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "role",
            "organization",
            "region",
            "status_ong",
            "status",
            "is_active",
            "must_change_password",
            "date_joined",
        ]

    def get_organization(self, obj):
        if obj.organization:
            return {
                "id": obj.organization.id,
                "name": obj.organization.name,
                "acronym": obj.organization.acronym,
                "email": obj.organization.email,
                "phone": obj.organization.phone,
            }
        return None

    def get_region(self, obj):
        return obj.organization.region if obj.organization else None

    def get_status_ong(self, obj):
        return obj.organization.status if obj.organization else None


@extend_schema(tags=["Accounts"], summary="Liste des gérunts (Super Admin)")
class GerantListView(generics.ListAPIView):
    """
    Liste de tous les gérunts de toutes les ONG. Réservé au Super Admin.
    """
    serializer_class = GerantWithOrganizationSerializer
    permission_classes = [IsAuthenticated, IsAccountActive, IsSuperAdmin]

    def get_queryset(self):
        return User.objects.filter(
            role=User.Role.GERANT,
            organization__isnull=False,
        ).select_related('organization').order_by('organization__name', 'last_name', 'first_name')
