import os
import re
from django.utils import timezone
from django.urls import reverse
from rest_framework import serializers
from .models import Budget, Don, Depense, Justification, Bailleur, Partenaire, LigneBudgetaire, Donateur, Financement
from .constants import FINANCE_CATEGORIES, FINANCE_CATEGORY_VALUES
from apps.common.scoping import reject_foreign_organization_payload
from apps.projects.models import Project
from apps.campaigns.models import Campaign
from apps.common.uploads import validate_document_upload
from apps.common.validators import validate_phone_senegal


def _scope_relation_fields(serializer, field_names, request):
    """Limit writable FK choices to the caller's ONG (Super Admin stays global)."""
    if not request or getattr(request.user, "role", None) == "SUPER_ADMIN":
        return
    organization_id = getattr(request.user, "organization_id", None)
    for name in field_names:
        field = serializer.fields.get(name)
        if field is not None and hasattr(field, "queryset"):
            field.queryset = (
                field.queryset.filter(organization_id=organization_id)
                if organization_id is not None else field.queryset.none()
            )


def _effective(serializer, attrs, field_name):
    if field_name in attrs:
        return attrs[field_name]
    return getattr(serializer.instance, field_name, None) if serializer.instance else None


def _assert_org(obj, expected_org_id, field_name):
    if obj is not None and obj.organization_id != expected_org_id:
        raise serializers.ValidationError({field_name: "Cette relation n'appartient pas à la même organisation."})


# =========================
# BUDGET
# =========================
class BudgetSerializer(serializers.ModelSerializer):
    date = serializers.DateField(required=True)
    projet_nom = serializers.CharField(source="projet.name", read_only=True)
    responsable_nom = serializers.SerializerMethodField()
    date_creation = serializers.DateTimeField(source="created_at", read_only=True)
    solde = serializers.ReadOnlyField()
    taux_execution = serializers.ReadOnlyField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _scope_relation_fields(self, ("projet",), self.context.get("request"))

    def get_responsable_nom(self, obj):
        if obj.created_by:
            return getattr(obj.created_by, "full_name", None) or obj.created_by.email
        return "Responsable Finance"

    class Meta:
        model = Budget
        fields = "__all__"
        read_only_fields = (
            "id",
            "organization",
            "created_by",
            "created_at",
            "updated_at",
            "solde",
            "taux_execution",
            "projet_nom",
            "responsable_nom",
            "date_creation",
        )

    def validate_montant(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Le montant doit être supérieur à 0."
            )
        return value

    def validate_date(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError("La date ne peut pas être dans le futur.")
        return value

    def validate_source_financement(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("La source de financement est obligatoire.")
        if not all(character.isalpha() or character == " " for character in value):
            raise serializers.ValidationError(
                "La source doit contenir uniquement des lettres et des espaces."
            )
        return value

    def validate_observation(self, value):
        value = (value or "").strip()
        if len(value) > 2000:
            raise serializers.ValidationError("L'observation ne peut pas dépasser 2 000 caractères.")
        return value

    def validate_projet(self, value):
        request = self.context.get("request")
        if request and getattr(request.user, "role", None) != "SUPER_ADMIN":
            if value.organization != request.user.organization:
                raise serializers.ValidationError(
                    "Le projet n'appartient pas à votre organisation."
                )
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        if request:
            reject_foreign_organization_payload(self.initial_data, request.user)
            if "statut" in self.initial_data and request.user.role not in {"GERANT", "SUPER_ADMIN"}:
                raise serializers.ValidationError({
                    "statut": "Seul le Gérant peut modifier le statut d'un budget."
                })
            project = _effective(self, attrs, "projet")
            organization_id = (
                self.instance.organization_id if self.instance else
                getattr(request.user, "organization_id", None)
            )
            if project and organization_id is not None:
                _assert_org(project, organization_id, "projet")
                if project.organization_id != organization_id:
                    raise serializers.ValidationError({"projet": "Le projet doit appartenir à l'organisation du budget."})
        return attrs


# =========================
# LIGNE BUDGETAIRE
# =========================
class LigneBudgetaireSerializer(serializers.ModelSerializer):
    budget_nom = serializers.CharField(source="budget.projet.name", read_only=True)
    budget = serializers.PrimaryKeyRelatedField(queryset=Budget.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _scope_relation_fields(self, ("budget",), self.context.get("request"))

    class Meta:
        model = LigneBudgetaire
        fields = "__all__"
        read_only_fields = ("id", "organization", "created_by", "created_at", "updated_at", "budget_nom")

    def validate_montant_prevu(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le montant prévu doit être supérieur à 0.")
        return value

    def validate_libelle(self, value):
        value = (value or "").strip()
        allowed_punctuation = set(" .,;:'’()&/+-")
        if not value:
            raise serializers.ValidationError("Le libellé est obligatoire.")
        if not any(character.isalpha() or character.isdigit() for character in value):
            raise serializers.ValidationError("Le libellé doit contenir au moins une lettre ou un chiffre.")
        if any(
            not (character.isalpha() or character.isdigit() or character.isspace() or character in allowed_punctuation)
            for character in value
        ):
            raise serializers.ValidationError("Le libellé contient un caractère non autorisé.")
        return value

    def validate_categorie(self, value):
        value = (value or "").strip()
        if value and value not in FINANCE_CATEGORY_VALUES:
            # Keep a legacy value editable on its own record without allowing new free-text categories.
            if not self.instance or value != self.instance.categorie:
                raise serializers.ValidationError("Sélectionnez une catégorie budgétaire autorisée.")
        return value

    def validate_montant_revise(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Le montant révisé doit être supérieur à 0.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        if request:
            reject_foreign_organization_payload(self.initial_data, request.user)
            budget = _effective(self, attrs, "budget")
            organization_id = (
                self.instance.organization_id if self.instance else
                getattr(request.user, "organization_id", None)
            )
            if budget:
                if organization_id is not None:
                    _assert_org(budget, organization_id, "budget")
                if budget.projet.organization_id != budget.organization_id:
                    raise serializers.ValidationError({"budget": "Le budget et son projet doivent appartenir à la même organisation."})
        return attrs


# =========================
# DONATEUR
# =========================
class DonateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donateur
        fields = "__all__"
        read_only_fields = ("id", "organization", "created_at", "updated_at")

    def validate_nom(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Le nom du donateur est obligatoire.")
        return value.strip()

    def validate(self, attrs):
        request = self.context.get("request")
        if request:
            reject_foreign_organization_payload(self.initial_data, request.user)
        return attrs


# =========================
# FINANCEMENT
# =========================
class FinancementSerializer(serializers.ModelSerializer):
    projet_nom = serializers.CharField(source="projet.name", read_only=True)
    bailleur_nom = serializers.CharField(source="bailleur.nom", read_only=True)
    budget_source = serializers.CharField(source="budget.source_financement", read_only=True)

    projet = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    budget = serializers.PrimaryKeyRelatedField(queryset=Budget.objects.all(), required=False, allow_null=True)
    campagne = serializers.PrimaryKeyRelatedField(queryset=Campaign.objects.all(), required=False, allow_null=True)
    bailleur = serializers.PrimaryKeyRelatedField(queryset=Bailleur.objects.all(), required=False, allow_null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _scope_relation_fields(self, ("projet", "budget", "campagne", "bailleur"), self.context.get("request"))

    class Meta:
        model = Financement
        fields = "__all__"
        read_only_fields = ("id", "reference", "organization", "created_by", "created_at", "updated_at", "projet_nom", "bailleur_nom", "budget_source")

    def validate_montant(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le montant du financement doit être supérieur à 0.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        if request:
            reject_foreign_organization_payload(self.initial_data, request.user)

        projet = _effective(self, attrs, "projet")
        budget = _effective(self, attrs, "budget")
        campagne = _effective(self, attrs, "campagne")
        bailleur = _effective(self, attrs, "bailleur")
        if projet and budget and budget.projet_id != projet.pk:
            raise serializers.ValidationError({"budget": "Le budget sélectionné n'appartient pas au projet spécifié."})
        organization_id = (
            self.instance.organization_id if self.instance else
            getattr(request.user, "organization_id", None) if request else None
        )
        relation_org_ids = {
            obj.organization_id for obj in (projet, budget, campagne, bailleur)
            if obj is not None
        }
        if organization_id is not None:
            relation_org_ids.add(organization_id)
        if len(relation_org_ids) > 1:
            raise serializers.ValidationError({"non_field_errors": "Toutes les relations du financement doivent appartenir à la même organisation."})
        if organization_id is not None:
            for field_name, obj in (("projet", projet), ("budget", budget), ("campagne", campagne), ("bailleur", bailleur)):
                _assert_org(obj, organization_id, field_name)
        if budget and budget.projet.organization_id != budget.organization_id:
            raise serializers.ValidationError({"budget": "Le budget et son projet doivent appartenir à la même organisation."})
        if campagne and projet and campagne.projet_id != projet.pk:
            raise serializers.ValidationError({"campagne": "La campagne ne dépend pas du projet indiqué."})
        if campagne and campagne.projet.organization_id != campagne.organization_id:
            raise serializers.ValidationError({"campagne": "La campagne et son projet doivent appartenir à la même organisation."})
        return attrs


# =========================
# DON
# =========================
class DonSerializer(serializers.ModelSerializer):
    date = serializers.DateField(required=True)
    donateur_nom = serializers.SerializerMethodField(read_only=True)
    campagne_nom = serializers.SerializerMethodField(read_only=True)

    donateur = serializers.PrimaryKeyRelatedField(queryset=Donateur.objects.all(), required=False, allow_null=True)
    campagne = serializers.PrimaryKeyRelatedField(queryset=Campaign.objects.all(), required=False, allow_null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _scope_relation_fields(self, ("donateur", "campagne"), self.context.get("request"))

    def get_donateur_nom(self, obj):
        try:
            return obj.donateur.nom if obj.donateur else None
        except Exception:
            return None

    def get_campagne_nom(self, obj):
        try:
            return obj.campagne.nom if obj.campagne else None
        except Exception:
            return None

    class Meta:
        model = Don
        fields = "__all__"
        read_only_fields = (
            "id",
            "reference",
            "organization",
            "created_by",
            "created_at",
            "updated_at",
            "donateur_nom",
            "campagne_nom",
        )

    def validate_montant(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Le montant doit être supérieur à 0."
            )
        return value

    def validate_date(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError("La date ne peut pas être dans le futur.")
        return value

    def validate_observation(self, value):
        value = (value or "").strip()
        if len(value) > 2000:
            raise serializers.ValidationError("L'observation ne peut pas dépasser 2 000 caractères.")
        return value

    def validate_donateur(self, value):
        if value is None:
            return value
        request = self.context.get("request")
        if request and getattr(request.user, "role", None) != "SUPER_ADMIN":
            if getattr(value, "organization", None) != request.user.organization:
                raise serializers.ValidationError("Le donateur n'appartient pas à votre organisation.")
        return value

    def validate_campagne(self, value):
        if value is None:
            return value
        request = self.context.get("request")
        if request and getattr(request.user, "role", None) != "SUPER_ADMIN":
            if getattr(value, "organization", None) != request.user.organization:
                raise serializers.ValidationError(
                    "La campagne n'appartient pas à votre organisation."
                )
        return value

    def validate_moyen_paiement(self, value):
        choix_valides = [c[0] for c in Don.MoyenPaiement.choices]
        if value not in choix_valides:
            raise serializers.ValidationError(
                f"Moyen de paiement invalide. Choisissez parmi : {', '.join(choix_valides)}."
            )
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        if request:
            reject_foreign_organization_payload(self.initial_data, request.user)
        donor = _effective(self, attrs, "donateur")
        campaign = _effective(self, attrs, "campagne")
        organization_id = (
            self.instance.organization_id if self.instance else
            getattr(request.user, "organization_id", None) if request else None
        )
        relation_org_ids = {
            obj.organization_id for obj in (donor, campaign) if obj is not None
        }
        if campaign is not None:
            relation_org_ids.add(campaign.projet.organization_id)
        if organization_id is not None:
            relation_org_ids.add(organization_id)
        if len(relation_org_ids) > 1:
            raise serializers.ValidationError({"non_field_errors": "Le donateur, la campagne et le don doivent appartenir à la même organisation."})
        if organization_id is not None:
            _assert_org(donor, organization_id, "donateur")
            _assert_org(campaign, organization_id, "campagne")
        if campaign and campaign.projet.organization_id != campaign.organization_id:
            raise serializers.ValidationError({"campagne": "La campagne et son projet doivent appartenir à la même organisation."})
        return attrs
        if value not in choix_valides:
            raise serializers.ValidationError(
                f"Moyen de paiement invalide. Choisissez parmi : {', '.join(choix_valides)}."
            )
        return value


# =========================
# DEPENSE
# =========================
class DepenseSerializer(serializers.ModelSerializer):
    date = serializers.DateField(required=True)
    projet_nom = serializers.SerializerMethodField(read_only=True)
    campagne_nom = serializers.SerializerMethodField(read_only=True)
    ligne_budgetaire_libelle = serializers.SerializerMethodField(read_only=True)
    justifications = serializers.SerializerMethodField(read_only=True)

    def get_projet_nom(self, obj):
        try:
            if obj.projet:
                return obj.projet.name
            if obj.budget and obj.budget.projet:
                return obj.budget.projet.name
            return None
        except Exception:
            return None

    def get_campagne_nom(self, obj):
        try:
            return obj.campagne.nom if obj.campagne else None
        except Exception:
            return None

    def get_ligne_budgetaire_libelle(self, obj):
        try:
            return obj.ligne_budgetaire.libelle if obj.ligne_budgetaire else None
        except Exception:
            return None

    def get_justifications(self, obj):
        return [
            {
                "id": str(j.id),
                "fichier": reverse("justification-document", kwargs={"id": j.id}) if j.fichier else None,
                "type_fichier": j.type_fichier,
                "statut": j.statut,
                "uploaded_by": j.uploaded_by.email if j.uploaded_by else None,
                "valide_par": j.valide_par.email if j.valide_par else None,
                "date_validation": j.date_validation.isoformat() if j.date_validation else None,
                "created_at": j.created_at.isoformat(),
            }
            for j in obj.justifications.all()
        ]

    budget = serializers.PrimaryKeyRelatedField(
        queryset=Budget.objects.all(),
        required=False,
        allow_null=True,
    )
    projet = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        required=False,
        allow_null=True,
    )
    ligne_budgetaire = serializers.PrimaryKeyRelatedField(
        queryset=LigneBudgetaire.objects.all(),
        required=False,
        allow_null=True,
    )
    campagne = serializers.PrimaryKeyRelatedField(
        queryset=Campaign.objects.all(),
        required=False,
        allow_null=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _scope_relation_fields(
            self,
            ("projet", "campagne", "budget", "ligne_budgetaire"),
            self.context.get("request"),
        )

    class Meta:
        model = Depense
        fields = "__all__"
        read_only_fields = (
            "id",
            "reference",
            "organization",
            "created_by",
            "created_at",
            "updated_at",
            "projet_nom",
            "campagne_nom",
            "ligne_budgetaire_libelle",
            "justifications",
        )

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, "copy") else dict(data)
        if "budget" in data and not data.get("budget"):
            data["budget"] = None
        if "projet" in data and not data.get("projet"):
            data["projet"] = None
        if "ligne_budgetaire" in data and not data.get("ligne_budgetaire"):
            data["ligne_budgetaire"] = None
        if "campagne" in data and not data.get("campagne"):
            data["campagne"] = None
        return super().to_internal_value(data)

    def validate_montant(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le montant doit être supérieur à 0.")
        return value

    def validate_date(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError("La date ne peut pas être dans le futur.")
        return value

    def validate_categorie(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("La catégorie est obligatoire.")
        if value not in FINANCE_CATEGORY_VALUES:
            if not self.instance or value != self.instance.categorie:
                raise serializers.ValidationError({
                    "categorie": "Sélectionnez une catégorie de dépense autorisée."
                })
        return value

    def validate_fournisseur(self, value):
        value = (value or "").strip()
        if len(value) > 255:
            raise serializers.ValidationError("Le fournisseur ne peut pas dépasser 255 caractères.")
        return value

    def validate_description(self, value):
        value = (value or "").strip()
        if len(value) > 2000:
            raise serializers.ValidationError("La description ne peut pas dépasser 2 000 caractères.")
        return value

    def validate_budget(self, value):
        if value is None:
            return value
        request = self.context.get("request")
        if request and getattr(request.user, "role", None) != "SUPER_ADMIN":
            if getattr(value, "organization", None) != request.user.organization:
                raise serializers.ValidationError("Le budget n'appartient pas à votre organisation.")
        return value

    def validate_campagne(self, value):
        if value is None:
            return value
        request = self.context.get("request")
        if request and getattr(request.user, "role", None) != "SUPER_ADMIN":
            if getattr(value, "organization", None) != request.user.organization:
                raise serializers.ValidationError("La campagne n'appartient pas à votre organisation.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        if request:
            reject_foreign_organization_payload(self.initial_data, request.user)
            if "statut" in self.initial_data and request.user.role not in {
                "FINANCE", "SUPER_ADMIN",
            }:
                raise serializers.ValidationError({
                    "statut": "Vous n'êtes pas autorisé à valider ou rejeter une dépense."
                })

        projet = _effective(self, attrs, "projet")
        budget = _effective(self, attrs, "budget")
        ligne_budgetaire = _effective(self, attrs, "ligne_budgetaire")
        campagne = _effective(self, attrs, "campagne")

        # Resolve the expected project through every supplied or existing link.
        linked_projects = [projet]
        if budget:
            linked_projects.append(budget.projet)
        if ligne_budgetaire:
            linked_projects.append(ligne_budgetaire.budget.projet)
        if campagne:
            linked_projects.append(campagne.projet)
        linked_projects = [linked for linked in linked_projects if linked is not None]
        if not linked_projects:
            raise serializers.ValidationError({
                "budget": "Associez la dépense à un budget, un projet, une campagne ou une ligne budgétaire."
            })
        if linked_projects and any(linked.pk != linked_projects[0].pk for linked in linked_projects[1:]):
            raise serializers.ValidationError({"non_field_errors": "Le projet, la campagne, le budget et la ligne budgétaire doivent désigner le même projet."})
        if ligne_budgetaire and budget and ligne_budgetaire.budget_id != budget.pk:
            raise serializers.ValidationError({"ligne_budgetaire": "La ligne budgétaire doit appartenir au budget de la dépense."})

        organization_ids = set()
        if self.instance:
            organization_ids.add(self.instance.organization_id)
        if request and getattr(request.user, "role", None) != "SUPER_ADMIN":
            user_org_id = getattr(request.user, "organization_id", None)
            if user_org_id is None:
                raise serializers.ValidationError({"organization": "Aucune organisation n'est associée à votre compte."})
            organization_ids.add(user_org_id)
        for obj in (projet, budget, ligne_budgetaire, campagne):
            if obj is not None:
                organization_ids.add(obj.organization_id)
        if len(organization_ids) > 1:
            raise serializers.ValidationError({"non_field_errors": "Toutes les relations doivent appartenir à la même organisation."})

        expected_org_id = next(iter(organization_ids), None)
        for field_name, obj in (("projet", projet), ("budget", budget), ("ligne_budgetaire", ligne_budgetaire), ("campagne", campagne)):
            if obj is not None and expected_org_id is not None:
                _assert_org(obj, expected_org_id, field_name)

        if budget and budget.projet.organization_id != budget.organization_id:
            raise serializers.ValidationError({"budget": "Le budget et son projet doivent appartenir à la même organisation."})
        if ligne_budgetaire:
            if ligne_budgetaire.budget.organization_id != ligne_budgetaire.organization_id:
                raise serializers.ValidationError({"ligne_budgetaire": "La ligne et son budget doivent appartenir à la même organisation."})
            if ligne_budgetaire.budget.projet.organization_id != ligne_budgetaire.budget.organization_id:
                raise serializers.ValidationError({"ligne_budgetaire": "Le budget de la ligne doit correspondre à son projet et organisation."})
        if campagne and campagne.projet.organization_id != campagne.organization_id:
            raise serializers.ValidationError({"campagne": "La campagne et son projet doivent appartenir à la même organisation."})

        return attrs


# =========================
# BAILLEUR
# =========================
class BailleurSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        error_messages={"invalid": "Veuillez saisir une adresse e-mail valide."},
    )
    type = serializers.CharField(required=True, allow_blank=False, max_length=100)

    class Meta:
        model = Bailleur
        fields = (
            "id", "nom", "type", "email", "telephone", "adresse", "actif",
            "organization", "created_at", "updated_at",
        )
        read_only_fields = ("id", "organization", "created_at", "updated_at")

    def validate_nom(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Le nom du bailleur est obligatoire.")
        return value.strip()

    def validate_telephone(self, value):
        if not value:
            return value
        try:
            return validate_phone_senegal(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc))

    def validate(self, attrs):
        request = self.context.get("request")
        if request:
            reject_foreign_organization_payload(self.initial_data, request.user)
        return attrs


# =========================
# PARTENAIRE
# =========================
class PartenaireSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        error_messages={"invalid": "Veuillez saisir une adresse e-mail valide."},
    )
    domaine = serializers.CharField(required=True, allow_blank=False, max_length=100)

    class Meta:
        model = Partenaire
        fields = (
            "id", "nom", "domaine", "email", "telephone", "adresse", "actif",
            "organization", "created_at", "updated_at",
        )
        read_only_fields = ("id", "organization", "created_at", "updated_at")

    def validate(self, attrs):
        request = self.context.get("request")
        if request:
            reject_foreign_organization_payload(self.initial_data, request.user)
        return attrs

    def validate_nom(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Le nom du partenaire est obligatoire.")
        return value.strip()

    def validate_telephone(self, value):
        if not value:
            return value
        try:
            return validate_phone_senegal(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc))


# =========================
# JUSTIFICATION
# =========================

# Extensions acceptées → type_fichier normalisé
EXTENSIONS_ACCEPTEES = {
    "pdf":  "pdf",
    "jpg":  "jpg",
    "jpeg": "jpg",   # normalisation : jpeg → jpg
    "png":  "png",
}

def detecter_type_fichier(fichier):
    """Détecte le type de fichier à partir de son extension."""
    if not fichier:
        return ""
    ext = os.path.splitext(fichier.name)[1].lower().lstrip(".")
    return EXTENSIONS_ACCEPTEES.get(ext, ext[:20])


class JustificationSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Justification
        fields = (
            "id",
            "depense",
            "fichier",
            "type_fichier",
            "statut",
            "uploaded_by",
            "created_at",
            "updated_at",
            "url",
        )
        read_only_fields = (
            "id",
            "depense",
            "uploaded_by",
            "statut",
            "created_at",
            "updated_at",
            "url",
        )

    def get_url(self, obj):
        if not obj.fichier:
            return None
        url = reverse("justification-document", kwargs={"id": obj.id})
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url

    def validate_fichier(self, value):
        try:
            return validate_document_upload(
                value,
                extensions=tuple(f".{extension}" for extension in EXTENSIONS_ACCEPTEES),
            )
        except Exception as exc:
            messages = getattr(exc, "messages", None)
            raise serializers.ValidationError(messages[0] if messages else "Le fichier est invalide.")

    def validate(self, attrs):
        # Auto-détecter type_fichier si non fourni ou vide
        fichier = attrs.get("fichier")
        type_fichier = attrs.get("type_fichier", "").strip()

        if fichier and not type_fichier:
            attrs["type_fichier"] = detecter_type_fichier(fichier)

        # Vérifier que type_fichier n'est pas vide après tentative de détection
        if not attrs.get("type_fichier"):
            raise serializers.ValidationError({
                "type_fichier": "Le type de fichier est requis (ex: pdf, jpg, png)."
            })

        return attrs
