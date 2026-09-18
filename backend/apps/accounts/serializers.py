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
            "is_active",
            "must_change_password",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "organization",
            "date_joined",
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


class RegisterAuthSerializer(serializers.Serializer):
    organization_name = serializers.CharField(max_length=200)
    organization_acronym = serializers.CharField(max_length=50, required=False, allow_blank=True)
    organization_email = serializers.EmailField()
    organization_phone = serializers.CharField(max_length=20)
    country = serializers.CharField(max_length=100, default="Sénégal")
    region = serializers.CharField(max_length=100)
    address = serializers.CharField(max_length=255)
    organization_description = serializers.CharField(required=False, allow_blank=True)
    logo = serializers.ImageField(required=False, allow_null=True)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)

    def validate(self, attrs):
        from apps.accounts.models import User
        from apps.organizations.models import Organization

        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError({"email": "Cet email est déjà utilisé."})
        if Organization.objects.filter(email=attrs["organization_email"]).exists():
            raise serializers.ValidationError({"organization_email": "Cet email ONG est déjà utilisé."})
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": "Les mots de passe ne correspondent pas."})
        return attrs


class ResendActivationSerializer(serializers.Serializer):
    email = serializers.EmailField()


class AgentListSerializer(serializers.ModelSerializer):
    """
    Vue minimale d'un agent terrain pour l'affectation de campagne.
    """

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "phone", "full_name", "role"]
        read_only_fields = fields

    def get_full_name(self, obj):
        return obj.full_name