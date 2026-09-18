from django.db import transaction
from django.utils import timezone

from rest_framework import serializers

from .models import Organization, Subscription
from apps.accounts.models import User, ActivationToken
from apps.accounts.services import create_gerant_for_organization
from apps.accounts.tasks import send_invitation_email


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"


class RegisterOrganizationSerializer(serializers.ModelSerializer):
    # Documents
    document_receipt = serializers.FileField(write_only=True, required=True)
    document_ninea = serializers.FileField(write_only=True, required=True)
    document_statutes = serializers.FileField(write_only=True, required=True)

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
            "document_receipt",
            "document_ninea",
            "document_statutes",
            "manager_first_name",
            "manager_last_name",
            "manager_email",
            "manager_phone",
        ]

    def validate_manager_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Cet email est déjà utilisé."
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("document_receipt", None)
        validated_data.pop("document_ninea", None)
        validated_data.pop("document_statutes", None)

        manager_data = {
            "first_name": validated_data.pop("manager_first_name"),
            "last_name": validated_data.pop("manager_last_name"),
            "email": validated_data.pop("manager_email"),
            "phone": validated_data.pop("manager_phone"),
        }

        organization = Organization.objects.create(
            **validated_data,
            status=Organization.Status.EN_ATTENTE,
            is_active=False,
        )

        documents = self.context.get("documents", {})
        if documents.get("receipt"):
            organization.document_receipt = documents["receipt"]
        if documents.get("ninea"):
            organization.document_ninea = documents["ninea"]
        if documents.get("statutes"):
            organization.document_statutes = documents["statutes"]
        organization.save(update_fields=["document_receipt", "document_ninea", "document_statutes", "updated_at"])

        user = create_gerant_for_organization(
            organization=organization,
            manager_first_name=manager_data["first_name"],
            manager_last_name=manager_data["last_name"],
            manager_email=manager_data["email"],
            manager_phone=manager_data["phone"],
        )

        return organization, user
