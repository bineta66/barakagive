from django.db import transaction

from rest_framework import serializers

from .models import Organization
from apps.accounts.services import create_gerant_for_organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"


class RegisterOrganizationSerializer(serializers.ModelSerializer):
    # Informations du premier Gérant
    manager_first_name = serializers.CharField(write_only=True)
    manager_last_name = serializers.CharField(write_only=True)
    manager_email = serializers.EmailField(write_only=True)
    manager_phone = serializers.CharField(write_only=True)

    class Meta:
        model = Organization
        fields = [
            "name",
            "acronym",
            "email",
            "phone",
            "address",
            "region",
            "country",
            "intervention_domain",
            "description",
            "logo",

            "manager_first_name",
            "manager_last_name",
            "manager_email",
            "manager_phone",
        ]

    def validate_manager_email(self, value):
        from apps.accounts.models import User
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Cet email est déjà utilisé."
            )
        return value

    @transaction.atomic
    def create(self, validated_data):

        manager_data = {
            "first_name": validated_data.pop("manager_first_name"),
            "last_name": validated_data.pop("manager_last_name"),
            "email": validated_data.pop("manager_email"),
            "phone": validated_data.pop("manager_phone"),
        }

        # Création de l'ONG
        organization = Organization.objects.create(
            **validated_data,
            status=Organization.Status.PENDING,
        )

        # Création automatique du Gérant + envoi de l'email d'activation
        create_gerant_for_organization(
            organization=organization,
            manager_first_name=manager_data["first_name"],
            manager_last_name=manager_data["last_name"],
            manager_email=manager_data["email"],
            manager_phone=manager_data["phone"],
        )

        return organization