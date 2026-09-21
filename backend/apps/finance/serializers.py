from rest_framework import serializers
from .models import Budget, Don, Depense, Justification


class BudgetSerializer(serializers.ModelSerializer):
    projet_nom = serializers.CharField(source='projet.name', read_only=True)
    solde = serializers.ReadOnlyField()
    taux_execution = serializers.ReadOnlyField()
    
    class Meta:
        model = Budget
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at", "solde", "taux_execution", "projet_nom"]


class DonSerializer(serializers.ModelSerializer):
    projet_nom = serializers.CharField(source='projet.name', read_only=True)
    campagne_nom = serializers.CharField(source='campagne.name', read_only=True)
    budget_source = serializers.CharField(source='budget.source_financement', read_only=True)
    
    class Meta:
        model = Don
        fields = "__all__"
        read_only_fields = ["id", "reference", "organization", "created_by", "created_at", "updated_at", "projet_nom", "campagne_nom", "budget_source"]


class DepenseSerializer(serializers.ModelSerializer):
    projet_nom = serializers.CharField(source='projet.name', read_only=True)
    campagne_nom = serializers.CharField(source='campagne.name', read_only=True)
    
    class Meta:
        model = Depense
        fields = "__all__"
        read_only_fields = ["id", "reference", "organization", "created_by", "created_at", "updated_at", "projet_nom", "campagne_nom"]


class JustificationSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Justification
        fields = ["id", "depense", "fichier", "type_fichier", "statut", "uploaded_by", "created_at", "updated_at", "url"]
        read_only_fields = ["id", "depense", "uploaded_by", "created_at", "updated_at", "url"]
    
    def get_url(self, obj):
        request = self.context.get("request")
        if not obj.fichier:
            return None
        url = obj.fichier.url
        return request.build_absolute_uri(url) if request else url