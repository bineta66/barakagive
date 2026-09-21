from rest_framework import serializers
from .models import Budget, Don, Depense, Justification


# =========================
# BUDGET
# =========================
class BudgetSerializer(serializers.ModelSerializer):
    projet_nom = serializers.CharField(source="projet.nom", read_only=True)
    solde = serializers.ReadOnlyField()
    taux_execution = serializers.ReadOnlyField()

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
        )

    def validate_montant(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Le montant doit être supérieur à 0."
            )
        return value


# =========================
# DON
# =========================
class DonSerializer(serializers.ModelSerializer):
    projet_nom = serializers.CharField(source="projet.nom", read_only=True)
    campagne_nom = serializers.CharField(source="campagne.nom", read_only=True)
    budget_source = serializers.CharField(
        source="budget.source_financement",
        read_only=True,
    )

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
            "projet_nom",
            "campagne_nom",
            "budget_source",
        )

    def validate(self, attrs):
        budget = attrs.get("budget")
        projet = attrs.get("projet")

        if budget and projet and budget.projet != projet:
            raise serializers.ValidationError({
                "budget": "Ce budget n'appartient pas au projet sélectionné."
            })

        return attrs

    def validate_montant(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Le montant doit être supérieur à 0."
            )
        return value


# =========================
# DEPENSE
# =========================
class DepenseSerializer(serializers.ModelSerializer):
    projet_nom = serializers.CharField(source="projet.nom", read_only=True)
    campagne_nom = serializers.CharField(source="campagne.nom", read_only=True)

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
        )

    def validate_montant(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Le montant doit être supérieur à 0."
            )
        return value


# =========================
# JUSTIFICATION
# =========================
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
            "uploaded_by",
            "created_at",
            "updated_at",
            "url",
        )

    def get_url(self, obj):
        request = self.context.get("request")

        if not obj.fichier:
            return None

        if request:
            return request.build_absolute_uri(obj.fichier.url)

        return obj.fichier.url

    def validate_fichier(self, value):
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError(
                "Le fichier ne doit pas dépasser 10 Mo."
            )
        return value