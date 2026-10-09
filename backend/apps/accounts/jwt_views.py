from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .models import User


class JWTLoginSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["role"] = user.role
        token["organization"] = (
            user.organization.id if user.organization else None
        )

        return token

    def validate(self, attrs):
        try:
            data = super().validate(attrs)
        except Exception:
            raise AuthenticationFailed(
                "Email ou mot de passe incorrect."
            )

        user = self.user

        if not user.is_active:
            raise AuthenticationFailed(
                "Votre compte n'est pas encore activé. Vérifiez votre email pour le lien d'activation."
            )

        if user.status != User.Status.ACTIVE:
            if user.status == User.Status.SUSPENDED:
                raise AuthenticationFailed(
                    "Votre compte a été suspendu. Contactez votre administrateur."
                )
            raise AuthenticationFailed(
                "Votre compte n'est pas encore activé. Vérifiez votre email pour le lien d'activation."
            )

        data["user"] = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role,
            "organization": (
                user.organization.id if user.organization else None
            ),
            "must_change_password": user.must_change_password,
        }
        data["must_change_password"] = user.must_change_password

        return data


class JWTLoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = JWTLoginSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = serializer.user
            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])

        return response


class ActiveTokenRefreshSerializer(TokenRefreshSerializer):
    """Reject refreshes when the account's current database status is inactive."""

    def validate(self, attrs):
        refresh = self.token_class(attrs["refresh"])
        user_id = refresh.payload.get(api_settings.USER_ID_CLAIM)
        user_model = get_user_model()
        try:
            user = user_model.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except (user_model.DoesNotExist, TypeError, ValueError):
            raise InvalidToken("Le compte associé à ce jeton est introuvable.")
        if not user.can_login:
            raise InvalidToken("Le compte associé à ce jeton est inactif ou suspendu.")
        return super().validate(attrs)


class ActiveTokenRefreshView(TokenRefreshView):
    serializer_class = ActiveTokenRefreshSerializer


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh = request.data.get("refresh")

        if refresh:
            try:
                token = RefreshToken(refresh)
                token.blacklist()
            except Exception:
                pass

        return Response(
            {"detail": "Déconnexion réussie."},
            status=status.HTTP_200_OK,
        )
