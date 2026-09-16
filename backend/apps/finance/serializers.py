from pathlib import Path

from django.db.models import Sum
from rest_framework import serializers

from apps.projects.models import Project

from .models import (
    Bailleur,
    Budget,
    Depense,
    Don,
    Justificatif,
    Partenaire,
    PosteBudgetaire,
)
from .services import create_depense, recalculate_poste


class OrganizationSerializerMixin:
    def validate_project_organization(self, project):
        user = self.context["request"].user
        if project.organization_id != user.organization_id:
            raise serializers.ValidationError("Le projet n'appartient pas à votre organisation.")
        return project


class BailleurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bailleur
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]


class PartenaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partenaire
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]


class DonSerializer(serializers.ModelSerializer):
    montant_restant = serializers.ReadOnlyField()

    class Meta:
        model = Don
        fields = "__all__"
        read_only_fields = [
            "id", "reference", "organization", "created_by", "created_at", "updated_at",
            "montant_affecte", "montant_restant",
        ]

    def validate_bailleur(self, bailleur):
        if bailleur.organization_id != self.context["request"].user.organization_id:
            raise serializers.ValidationError("Le bailleur n'appartient pas à votre organisation.")
        return bailleur


class PosteBudgetaireSerializer(serializers.ModelSerializer):
    montant_restant = serializers.ReadOnlyField()

    class Meta:
        model = PosteBudgetaire
        fields = "__all__"
        read_only_fields = ["id", "montant_depense", "montant_restant", "created_at", "updated_at"]

    def validate(self, attrs):
        budget = attrs.get("budget") or self.instance.budget
        montant = attrs.get("montant", self.instance.montant if self.instance else 0)
        current = budget.postes.exclude(pk=self.instance.pk).aggregate(total=Sum("montant"))["total"] or 0
        if current + montant > budget.montant_total:
            raise serializers.ValidationError("La somme des postes dépasse le budget.")
        return attrs


class BudgetSerializer(serializers.ModelSerializer):
    postes = PosteBudgetaireSerializer(many=True, read_only=True)

    class Meta:
        model = Budget
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at", "postes"]

    def validate(self, attrs):
        user = self.context["request"].user
        projet = attrs.get("projet", self.instance.projet if self.instance else None)
        don = attrs.get("don", self.instance.don if self.instance else None)
        if projet and projet.organization_id != user.organization_id:
            raise serializers.ValidationError("Le projet n'appartient pas à votre organisation.")
        if don and don.organization_id != user.organization_id:
            raise serializers.ValidationError("Le don n'appartient pas à votre organisation.")
        montant = attrs.get("montant_total", self.instance.montant_total if self.instance else 0)
        if don and montant > don.montant_restant + (self.instance.montant_total if self.instance and self.instance.don_id == don.id else 0):
            raise serializers.ValidationError("Le budget dépasse le montant restant du don.")
        return attrs


class JustificatifSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Justificatif
        fields = ["id", "depense", "fichier", "nom_original", "type_fichier", "taille", "uploaded_by", "created_at", "url"]
        read_only_fields = ["id", "depense", "nom_original", "type_fichier", "taille", "uploaded_by", "created_at", "url"]

    def validate_fichier(self, fichier):
        extension = Path(fichier.name).suffix.lower()
        if extension not in {".pdf", ".jpg", ".jpeg", ".png"}:
            raise serializers.ValidationError("Format autorisé : PDF, JPG, JPEG ou PNG.")
        if fichier.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("La taille maximale est de 10 Mo.")
        return fichier

    def get_url(self, obj):
        request = self.context.get("request")
        if not obj.fichier:
            return None
        url = obj.fichier.url
        return request.build_absolute_uri(url) if request else url

    def create(self, validated_data):
        fichier = validated_data["fichier"]
        validated_data.update(
            nom_original=fichier.name,
            type_fichier=Path(fichier.name).suffix[1:].upper(),
            taille=fichier.size,
        )
        return super().create(validated_data)


class DepenseSerializer(serializers.ModelSerializer):
    justificatifs = JustificatifSerializer(many=True, read_only=True)
    fichier = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = Depense
        fields = "__all__"
        read_only_fields = ["id", "reference", "organization", "created_by", "created_at", "updated_at", "statut", "justificatifs"]

    def validate_fichier(self, fichier):
        extension = Path(fichier.name).suffix.lower()
        if extension not in {".pdf", ".jpg", ".jpeg", ".png"}:
            raise serializers.ValidationError("Format autorisé : PDF, JPG, JPEG ou PNG.")
        if fichier.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("La taille maximale est de 10 Mo.")
        return fichier

    def validate(self, attrs):
        user = self.context["request"].user
        poste = attrs.get("poste_budgetaire", self.instance.poste_budgetaire if self.instance else None)
        projet = attrs.get("projet", self.instance.projet if self.instance else None)
        if poste and poste.budget.organization_id != user.organization_id:
            raise serializers.ValidationError("Le poste budgétaire n'appartient pas à votre organisation.")
        if projet and projet.organization_id != user.organization_id:
            raise serializers.ValidationError("Le projet n'appartient pas à votre organisation.")
        return attrs

    def create(self, validated_data):
        fichier = validated_data.pop("fichier", None)
        depense = create_depense(validated_data, self.context["request"].user, bool(fichier))
        if fichier:
            Justificatif.objects.create(
                depense=depense,
                fichier=fichier,
                nom_original=fichier.name,
                type_fichier=Path(fichier.name).suffix[1:].upper(),
                taille=fichier.size,
                uploaded_by=self.context["request"].user,
            )
        return depense