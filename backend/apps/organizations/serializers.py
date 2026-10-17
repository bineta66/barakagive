from django.db import transaction

from rest_framework import serializers
from django.urls import reverse

from .models import Organization
from apps.accounts.models import User
from apps.accounts.services import create_gerant_for_organization
from apps.common.validators import (
    validate_nom, validate_nom_long, validate_email,
    validate_phone_senegal, validate_description, validate_adresse,
)
from apps.common.uploads import validate_image_upload, validate_pdf_upload


class OrganizationSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(
        required=False,
        allow_null=True,
        validators=[validate_image_upload],
    )
    document_receipt = serializers.FileField(
        required=False, allow_null=True, validators=[validate_pdf_upload]
    )
    document_ninea = serializers.FileField(
        required=False, allow_null=True, validators=[validate_pdf_upload]
    )
    document_statutes = serializers.FileField(
        required=False, allow_null=True, validators=[validate_pdf_upload]
    )

    class Meta:
        model = Organization
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if instance.pk:
            for field_name in ("document_receipt", "document_ninea", "document_statutes"):
                if getattr(instance, field_name, None):
                    url = reverse("organizations:document", kwargs={"pk": instance.pk, "document_type": field_name})
                    data[field_name] = request.build_absolute_uri(url) if request else url
        return data

    def validate_name(self, value):
        try:
            return validate_nom_long(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc))

    def validate_email(self, value):
        try:
            return validate_email(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc))

    def validate_phone(self, value):
        try:
            return validate_phone_senegal(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc))

    def validate_address(self, value):
        try:
            return validate_adresse(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc))

    def validate_description(self, value):
        value = (value or "").strip()
        try:
            return validate_description(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc))

    def validate_acronym(self, value):
        value = (value or "").strip()
        if len(value) > 50:
            raise serializers.ValidationError("L'acronyme ne peut pas dépasser 50 caractères.")
        return value

    def validate_region(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("La région est obligatoire.")
        return value

    def validate_country(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Le pays est obligatoire.")
        return value

    def validate_intervention_domain(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Le domaine d'intervention est obligatoire.")
        return value


class RegisterOrganizationSerializer(serializers.ModelSerializer):
    document_receipt  = serializers.FileField(write_only=True, required=True, validators=[validate_pdf_upload])
    document_ninea    = serializers.FileField(write_only=True, required=True, validators=[validate_pdf_upload])
    document_statutes = serializers.FileField(write_only=True, required=True, validators=[validate_pdf_upload])

    manager_first_name = serializers.CharField(write_only=True)
    manager_last_name  = serializers.CharField(write_only=True)
    manager_email      = serializers.EmailField(write_only=True)
    manager_phone      = serializers.CharField(write_only=True)

    class Meta:
        model = Organization
        fields = [
            "name", "acronym", "email", "phone", "address",
            "region", "country", "intervention_domain", "description",
            "document_receipt", "document_ninea", "document_statutes",
            "manager_first_name", "manager_last_name", "manager_email", "manager_phone",
        ]

    # ── Validation des champs ONG ────────────────────────────────────────────
    def validate_name(self, value):
        try:
            return validate_nom_long(value)
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

    def validate_description(self, value):
        if not value:
            return value
        try:
            return validate_description(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def validate_address(self, value):
        if not value:
            return value
        try:
            return validate_adresse(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def validate_acronym(self, value):
        value = (value or "").strip()
        if len(value) > 50:
            raise serializers.ValidationError("L'acronyme ne peut pas dépasser 50 caractères.")
        return value

    def validate_region(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("La région est obligatoire.")
        return value

    def validate_country(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Le pays est obligatoire.")
        return value

    def validate_intervention_domain(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Le domaine d'intervention est obligatoire.")
        return value

    # ── Validation du gérant ─────────────────────────────────────────────────
    def validate_manager_first_name(self, value):
        try:
            return validate_nom(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def validate_manager_last_name(self, value):
        try:
            return validate_nom(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def validate_manager_email(self, value):
        try:
            v = validate_email(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        if User.objects.filter(email=v).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return v

    def validate_manager_phone(self, value):
        if not value:
            return value
        try:
            return validate_phone_senegal(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("document_receipt", None)
        validated_data.pop("document_ninea", None)
        validated_data.pop("document_statutes", None)

        manager_data = {
            "first_name": validated_data.pop("manager_first_name"),
            "last_name":  validated_data.pop("manager_last_name"),
            "email":      validated_data.pop("manager_email"),
            "phone":      validated_data.pop("manager_phone"),
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
        organization.save(update_fields=[
            "document_receipt", "document_ninea", "document_statutes", "updated_at"
        ])

        user = create_gerant_for_organization(
            organization=organization,
            manager_first_name=manager_data["first_name"],
            manager_last_name=manager_data["last_name"],
            manager_email=manager_data["email"],
            manager_phone=manager_data["phone"],
        )

        return organization, user


class AIVerificationReportSerializer(serializers.ModelSerializer):
    """Serializer pour le rapport de vérification IA (lecture seule)."""

    class Meta:
        from .models import AIVerificationReport
        model = AIVerificationReport
        fields = [
            "id",
            "score_confiance",
            "statut_ia",
            "nom_extrait",
            "ninea_extrait",
            "recepisse_extrait",
            "documents",
            "observation",
            "recommandation",
            "anomalies",
            "created_at",
        ]
        read_only_fields = fields


class OrganisationRequestSerializer(serializers.ModelSerializer):
    """Serializer pour la lecture d'une demande d'inscription ONG."""

    gerant = serializers.SerializerMethodField()
    gerant_nom = serializers.SerializerMethodField()
    gerant_prenom = serializers.SerializerMethodField()
    gerant_email = serializers.SerializerMethodField()
    gerant_telephone = serializers.SerializerMethodField()
    recepisse_pdf = serializers.SerializerMethodField()
    ninea_pdf = serializers.SerializerMethodField()
    statuts_pdf = serializers.SerializerMethodField()

    class Meta:
        from .models import OrganisationRequest
        model = OrganisationRequest
        fields = [
            "id",
            "nom_ong",
            "sigle",
            "domaine",
            "region",
            "adresse",
            "email",
            "telephone",
            "gerant",
            "gerant_prenom",
            "gerant_nom",
            "gerant_email",
            "gerant_telephone",
            "recepisse_pdf",
            "ninea_pdf",
            "statuts_pdf",
            "statut",
            "ai_report",
            "motif_rejet",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def _get_manager(self, obj):
        if hasattr(obj, "_cached_manager"):
            return obj._cached_manager
        manager = None
        if hasattr(obj, "users"):
            manager = obj.users.filter(role=User.Role.GERANT).first() or obj.users.first()
        obj._cached_manager = manager
        return manager

    def get_gerant(self, obj):
        prenom = getattr(obj, "gerant_prenom", "")
        nom = getattr(obj, "gerant_nom", "")
        if not prenom and not nom:
            m = self._get_manager(obj)
            if m:
                prenom = m.first_name
                nom = m.last_name
        full = f"{prenom} {nom}".strip()
        return full or "—"

    def get_gerant_prenom(self, obj):
        val = getattr(obj, "gerant_prenom", "")
        if not val:
            m = self._get_manager(obj)
            if m:
                return m.first_name
        return val

    def get_gerant_nom(self, obj):
        val = getattr(obj, "gerant_nom", "")
        if not val:
            m = self._get_manager(obj)
            if m:
                return m.last_name
        return val

    def get_gerant_email(self, obj):
        val = getattr(obj, "gerant_email", "")
        if not val:
            m = self._get_manager(obj)
            if m:
                return m.email
            return getattr(obj, "email", "")
        return val

    def get_gerant_telephone(self, obj):
        val = getattr(obj, "gerant_telephone", "")
        if not val:
            m = self._get_manager(obj)
            if m:
                return getattr(m, "phone", "") or ""
            return getattr(obj, "telephone", "")
        return val

    def _resolve_file_url(self, file_field):
        if not file_field:
            return None
        try:
            if hasattr(file_field, "url") and file_field.url:
                request = self.context.get("request")
                if request:
                    return request.build_absolute_uri(file_field.url)
                return file_field.url
        except Exception:
            pass
        if isinstance(file_field, str) and file_field:
            return file_field
        return None

    def get_recepisse_pdf(self, obj):
        return self._private_request_document_url(obj, "recepisse_pdf")

    def get_ninea_pdf(self, obj):
        return self._private_request_document_url(obj, "ninea_pdf")

    def get_statuts_pdf(self, obj):
        return self._private_request_document_url(obj, "statuts_pdf")

    def _private_request_document_url(self, obj, field_name):
        if not getattr(obj, field_name, None):
            return None
        url = reverse("superadmin-organisation-document", kwargs={"pk": obj.pk, "document_type": field_name})
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url


class OrganisationRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'une demande d'inscription ONG (POST)."""

    recepisse_pdf = serializers.FileField(required=True, validators=[validate_pdf_upload])
    ninea_pdf = serializers.FileField(required=True, validators=[validate_pdf_upload])
    statuts_pdf = serializers.FileField(required=True, validators=[validate_pdf_upload])

    class Meta:
        from .models import OrganisationRequest
        model = OrganisationRequest
        fields = [
            "nom_ong",
            "sigle",
            "domaine",
            "region",
            "adresse",
            "email",
            "telephone",
            "gerant_prenom",
            "gerant_nom",
            "gerant_email",
            "gerant_telephone",
            "recepisse_pdf",
            "ninea_pdf",
            "statuts_pdf",
        ]
