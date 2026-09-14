from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Affichage des informations d'un utilisateur.
    """

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
            "status",
        ]
        read_only_fields = [
            "id",
            "organization",
            "status",
        ]


class CreateUserSerializer(serializers.ModelSerializer):
    """
    Création d'un utilisateur par le Gérant.
    Le mot de passe sera défini lors de l'activation.
    """

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "role",
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Un utilisateur avec cet email existe déjà."
            )
        return value

    def validate_role(self, value):
        roles_autorises = [
            User.Role.CHEF_PROJET,
            User.Role.FINANCE,
            User.Role.AGENT,
        ]

        if value not in roles_autorises:
            raise serializers.ValidationError(
                "Le Gérant peut uniquement créer un Chef de projet, un Responsable Finance ou un Agent Terrain."
            )

        return value


class ActivateAccountSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Les mots de passe ne correspondent pas."}
            )
        return attrs