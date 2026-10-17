import uuid
from django.contrib.auth.tokens import default_token_generator
from django.core import signing
from rest_framework import serializers

from .models import User
from apps.common.validators import (
    validate_nom,
    validate_email,
    validate_phone_senegal,
    validate_password_strong,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "first_name", "last_name", "email", "phone",
            "role", "organization", "status", "is_active",
            "must_change_password", "date_joined",
        ]
        # Rôle et organisation sont déterminés par le backend, jamais par le
        # payload d'un utilisateur. Cette protection s'applique également au
        # PUT générique hérité par UserDetailView.
        read_only_fields = [
            "id",
            "organization",
            "role",
            "status",
            "is_active",
            "date_joined",
            "is_staff",
            "is_superuser",
            "must_change_password",
        ]

    def validate_first_name(self, value):
        try:
            return validate_nom(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc))

    def validate_last_name(self, value):
        try:
            return validate_nom(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc))

    def validate_email(self, value):
        try:
            normalized = validate_email(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc))
        queryset = User.objects.filter(email__iexact=normalized)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Un utilisateur avec cet email existe déjà.")
        return normalized

    def validate_phone(self, value):
        if not value:
            return value
        try:
            return validate_phone_senegal(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc))


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "role"]

    def validate(self, attrs):
        protected_fields = {
            "organization",
            "organization_id",
            "is_staff",
            "is_superuser",
            "is_super_admin",
            "username",
        }
        attempted = protected_fields.intersection(self.initial_data.keys())
        if attempted:
            raise serializers.ValidationError({
                "detail": "Ces champs ne peuvent pas être fournis lors de la création.",
                "fields": sorted(attempted),
            })
        return attrs

    def validate_first_name(self, value):
        try:
            return validate_nom(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def validate_last_name(self, value):
        try:
            return validate_nom(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def validate_email(self, value):
        try:
            v = validate_email(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        if User.objects.filter(email=v).exists():
            raise serializers.ValidationError("Un utilisateur avec cet email existe déjà.")
        return v

    def validate_phone(self, value):
        if not value:
            return value
        try:
            return validate_phone_senegal(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def validate_role(self, value):
        roles_autorises = [User.Role.CHEF_PROJET, User.Role.FINANCE, User.Role.AGENT]
        if value not in roles_autorises:
            raise serializers.ValidationError(
                "Le Gérant peut uniquement créer un Chef de projet, un Responsable Finance ou un Agent Terrain."
            )
        return value


class ActivateAccountSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, required=False)

    def validate_token(self, value):
        v = str(value).strip().strip('"').strip("'")
        try:
            return uuid.UUID(v)
        except (ValueError, TypeError):
            raise serializers.ValidationError("Le format du jeton d'activation est invalide.")

    def validate_password(self, value):
        if not value or len(value) < 8:
            raise serializers.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        try:
            return validate_password_strong(value)
        except Exception:
            raise serializers.ValidationError(
                "Le mot de passe doit contenir au moins 8 caractères, dont 1 majuscule, 1 minuscule, 1 chiffre et 1 caractère spécial (@$!%*?&_-#^)."
            )

    def validate(self, attrs):
        confirm = attrs.get("password_confirm")
        if confirm and attrs.get("password") != confirm:
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

    def validate_first_name(self, value):
        try:
            return validate_nom(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def validate_last_name(self, value):
        try:
            return validate_nom(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def validate_email(self, value):
        try:
            return validate_email(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def validate_phone(self, value):
        if not value:
            return value
        try:
            return validate_phone_senegal(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))

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

    def validate_new_password(self, value):
        try:
            return validate_password_strong(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "Les mots de passe ne correspondent pas."}
            )
        return attrs


class ResendActivationSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=1000)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    def validate_password(self, value):
        try:
            return validate_password_strong(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc))

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({
                "password_confirm": "Les mots de passe ne correspondent pas."
            })
        try:
            payload = signing.loads(
                attrs["token"],
                salt="barakagive.password-reset",
                max_age=3600,
            )
            user = User.objects.get(pk=payload["uid"], is_active=True)
        except (signing.BadSignature, signing.SignatureExpired, KeyError, User.DoesNotExist, TypeError):
            raise serializers.ValidationError({"token": "Le lien de réinitialisation est invalide ou expiré."})
        if not user.can_login:
            raise serializers.ValidationError({"token": "Le lien de réinitialisation est invalide ou expiré."})
        if not default_token_generator.check_token(user, payload.get("reset_token", "")):
            raise serializers.ValidationError({"token": "Le lien de réinitialisation est invalide ou expiré."})
        attrs["user"] = user
        return attrs


class AgentListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "phone", "full_name", "role"]
        read_only_fields = fields

    def get_full_name(self, obj):
        return obj.full_name
