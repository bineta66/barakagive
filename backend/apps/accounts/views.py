from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from .models import User
from .serializers import (
    UserSerializer,
    CreateUserSerializer,
    ActivateAccountSerializer,
)
from .permissions import (
    IsAccountActive,
    IsGerant,
)
from .services import (
    create_user_by_manager,
    activate_account,
)


@extend_schema(tags=["Accounts"], summary="Activer un compte")
class ActivateAccountView(generics.GenericAPIView):
    """
    Activation du compte avec le token reçu.
    """
    serializer_class = ActivateAccountSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            activate_account(
                token=serializer.validated_data["token"],
                password=serializer.validated_data["password"],
            )
        except ValidationError as e:
            detail = e.detail
            if isinstance(detail, list):
                detail = detail[0]
            return Response(
                {"detail": detail},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Compte activé avec succès."},
            status=status.HTTP_200_OK,
        )


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

    def get_queryset(self):
        return User.objects.filter(
            organization=self.request.user.organization
        ).order_by("first_name")


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