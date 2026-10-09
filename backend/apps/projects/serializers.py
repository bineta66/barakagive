from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers

from apps.accounts.models import User
from apps.common.scoping import reject_foreign_organization_payload
from apps.common.validators import (
    validate_nom_long, validate_description,
)
from apps.forms.models import FormField
from .models import Project, ProjectCriteria


def _sync_project_allocation(project, amount, user):
    """Persist the project's editable allocation as one tagged finance budget."""
    from apps.finance.models import Budget

    allocation = Budget.objects.filter(
        projet=project,
        organization=project.organization,
        source_financement="Allocation projet",
    ).order_by("created_at").first()
    if allocation:
        allocation.montant = amount
        allocation.save(update_fields=["montant", "updated_at"])
        return
    if amount == 0:
        return
    defaults = {
        "montant": amount,
        "date": timezone.localdate(),
        "created_by": user,
    }
    Budget.objects.create(
        projet=project,
        organization=project.organization,
        source_financement="Allocation projet",
        **defaults,
    )


class ProjectBudgetField(serializers.Field):
    def get_attribute(self, instance):
        return instance

    def to_internal_value(self, data):
        field = serializers.DecimalField(
            max_digits=15,
            decimal_places=2,
            min_value=Decimal("0"),
            max_value=Decimal("9999999999999.99"),
        )
        try:
            return field.run_validation(data)
        except serializers.ValidationError:
            raise

    def to_representation(self, project):
        return project.budgets.aggregate(total=Sum("montant"))["total"] or Decimal("0.00")


class ProjectCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCriteria
        fields = "__all__"
        read_only_fields = ["created_by", "created_at"]


class ProjectCriteriaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCriteria
        fields = ["nom", "poids", "question", "vulnerable_values", "vulnerable_operator"]
        read_only_fields = ["created_by"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        project = self.context.get("projet") or getattr(self.instance, "projet", None)
        question_field = self.fields.get("question")
        if question_field is not None and hasattr(question_field, "queryset"):
            if project is not None:
                question_field.queryset = FormField.objects.filter(
                    formulaire__campagne__projet=project,
                    formulaire__organization_id=project.organization_id,
                )
            elif request is not None:
                question_field.queryset = question_field.queryset.none()

    def validate_nom(self, value):
        v = (value or "").strip()
        if not v:
            raise serializers.ValidationError("Le nom du critère est obligatoire.")
        if len(v) < 2:
            raise serializers.ValidationError("Le nom du critère doit contenir au moins 2 caractères.")
        return v

    def validate_poids(self, value):
        if value is None or value < 1 or value > 100:
            raise serializers.ValidationError("Le poids doit être un entier entre 1 et 100.")
        return value

    def validate(self, attrs):
        project = self.context.get("projet") or getattr(self.instance, "projet", None)
        if project is None:
            return attrs
        current = ProjectCriteria.objects.filter(projet=project, actif=True)
        if self.instance:
            current = current.exclude(pk=self.instance.pk)
        nom = attrs.get("nom", getattr(self.instance, "nom", "")).strip()
        if nom and current.filter(nom__iexact=nom).exists():
            raise serializers.ValidationError({
                "nom": "Un critère portant ce nom existe déjà pour ce projet."
            })
        total = sum(current.values_list("poids", flat=True)) + attrs.get(
            "poids", getattr(self.instance, "poids", 0)
        )
        if total > 100:
            raise serializers.ValidationError({
                "poids": "La somme des poids des critères ne peut pas dépasser 100 %."
            })
        question = attrs.get("question", getattr(self.instance, "question", None))
        if question:
            if (
                question.formulaire.campagne.projet_id != project.pk
                or question.formulaire.organization_id != project.organization_id
            ):
                raise serializers.ValidationError({
                    "question": "La question doit appartenir à un formulaire du même projet et de la même organisation."
                })
            if question.critere_id and (
                self.instance is None or question.critere_id != self.instance.pk
            ):
                raise serializers.ValidationError({
                    "question": "Cette question est déjà rattachée à un autre critère."
                })
            if question.criteria.exclude(pk=self.instance.pk if self.instance else None).exists():
                raise serializers.ValidationError({
                    "question": "Cette question est définie comme question principale d'un autre critère."
                })
        return attrs

    def create(self, validated_data):
        if "projet" not in validated_data:
            validated_data["projet"] = self.context.get("projet")
        if "created_by" not in validated_data:
            request = self.context.get("request")
            if request and request.user:
                validated_data["created_by"] = request.user
        return super().create(validated_data)


class ProjectSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=False, allow_blank=True)
    chef_projet        = serializers.ReadOnlyField(source="chef_projet.email")
    responsable_finance = serializers.ReadOnlyField(source="responsable_finance.email")
    organization       = serializers.ReadOnlyField(source="organization.name")
    criteres           = ProjectCriteriaSerializer(many=True, read_only=True)
    budget = ProjectBudgetField(required=False)

    def validate_name(self, value):
        try:
            return validate_nom_long(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc))

    def validate_description(self, value):
        if not value:
            return ""
        try:
            return validate_description(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc))

    def validate_objectif(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("L'objectif humanitaire est obligatoire.")
        if len(value) > 2000:
            raise serializers.ValidationError("L'objectif ne peut pas dépasser 2 000 caractères.")
        return value

    def validate_region(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("La région est obligatoire.")
        if len(value) > 100:
            raise serializers.ValidationError("La région ne peut pas dépasser 100 caractères.")
        return value

    def validate(self, attrs):
        # PATCH doit vérifier la paire effective, en combinant la date envoyée
        # avec celle déjà enregistrée.
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({
                "end_date": "La date de fin doit être égale ou postérieure à la date de début."
            })
        request = self.context.get("request")
        if request:
            reject_foreign_organization_payload(self.initial_data, request.user)
        return attrs

    class Meta:
        model = Project
        fields = [
            "id", "name", "code", "description", "region", "objectif",
            "start_date", "end_date", "chef_projet", "responsable_finance",
            "organization", "created_by", "created_at", "updated_at", "archived", "criteres", "budget",
        ]
        read_only_fields = ["id", "code", "created_by", "created_at", "updated_at", "archived"]

    def update(self, instance, validated_data):
        budget = validated_data.pop("budget", None)
        project = super().update(instance, validated_data)
        if budget is not None:
            request = self.context.get("request")
            _sync_project_allocation(project, budget, getattr(request, "user", None))
        return project


class ProjectCreateSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=False, allow_blank=True)
    budget = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal("0"),
        max_value=Decimal("9999999999999.99"),
        required=False,
        default=Decimal("0"),
    )
    chef_projet = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True,
    )
    responsable_finance = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True,
    )
    criteres = ProjectCriteriaCreateSerializer(many=True, write_only=True, required=True, allow_empty=False)

    class Meta:
        model = Project
        fields = [
            "name", "description", "region", "objectif", "start_date", "end_date",
            "chef_projet", "responsable_finance", "criteres", "code",
            "organization", "created_by", "budget",
        ]
        read_only_fields = ["code", "organization", "created_by"]

    def validate_name(self, value):
        try:
            return validate_nom_long(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def validate_description(self, value):
        if not value:
            return value
        try:
            return validate_description(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def validate_objectif(self, value):
        v = (value or "").strip()
        if not v:
            raise serializers.ValidationError("L'objectif humanitaire est obligatoire.")
        if len(v) > 2000:
            raise serializers.ValidationError("L'objectif ne peut pas dépasser 2 000 caractères.")
        return v

    def validate_region(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("La région est obligatoire.")
        if len(value) > 100:
            raise serializers.ValidationError("La région ne peut pas dépasser 100 caractères.")
        return value

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        org = getattr(getattr(request, "user", None), "organization", None)
        if org is not None:
            org_users = User.objects.filter(organization=org)
            self.fields["chef_projet"].queryset = org_users.filter(role=User.Role.CHEF_PROJET)
            self.fields["responsable_finance"].queryset = org_users.filter(role=User.Role.FINANCE)

    def validate(self, attrs):
        request = self.context.get("request")
        if request:
            reject_foreign_organization_payload(self.initial_data, request.user)
        # Validation date fin >= date début
        start_date = attrs.get("start_date")
        end_date   = attrs.get("end_date")
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({
                "end_date": "La date de fin doit être postérieure à la date de début."
            })

        # Validation somme poids critères = 100
        criteres = attrs.get("criteres", [])
        if criteres:
            noms = [" ".join(c.get("nom", "").split()).casefold() for c in criteres if c.get("nom")]
            if len(noms) != len(set(noms)):
                raise serializers.ValidationError({"criteres": "Les noms des critères doivent être uniques pour un projet."})
            total_poids = sum(int(c.get("poids", 0)) for c in criteres)
            if total_poids != 100:
                raise serializers.ValidationError({
                    "criteres": (
                        f"La somme des poids des critères doit être exactement 100. "
                        f"Total actuel : {total_poids}."
                    )
                })
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]
        criteres_data = validated_data.pop("criteres", [])
        budget = validated_data.pop("budget", Decimal("0"))
        project = Project.objects.create(
            **validated_data,
            organization=request.user.organization,
            created_by=request.user,
        )
        for critere_data in criteres_data:
            ProjectCriteria.objects.create(
                projet=project, created_by=request.user, **critere_data,
            )
        if budget > 0:
            _sync_project_allocation(project, budget, request.user)
        return project


class BudgetUpdateSerializer(serializers.Serializer):
    budget = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal("0"),
        max_value=Decimal("9999999999999.99"),
    )

    def validate_budget(self, value):
        if value < 0:
            raise serializers.ValidationError("Le budget doit être supérieur ou égal à 0.")
        return value
