from rest_framework import serializers

from apps.projects.models import Project
from apps.zones.models import Zone
from apps.accounts.models import User
from .models import Campaign


class ZoneSummarySerializer(serializers.ModelSerializer):
    """Sérialiseur minimal pour les zones dans les listes."""

    class Meta:
        model = Zone
        fields = ["id", "nom", "region", "departement"]


class ProjectSummarySerializer(serializers.ModelSerializer):
    """Sérialiseur minimal pour le projet dans les détails de campagne."""

    chef_projet = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ["id", "code", "name", "region", "chef_projet"]

    def get_chef_projet(self, obj):
        return {
            "id": obj.chef_projet.id,
            "email": obj.chef_projet.email,
            "full_name": obj.chef_projet.full_name,
        }


class CampaignListSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la liste des campagnes.
    Accessible à GERANT et CHEF_PROJET.
    """

    projet = serializers.SerializerMethodField()
    zones_count = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            "id",
            "code_campagne",
            "nom",
            "projet",
            "zones_count",
            "date_debut",
            "date_fin",
        ]

    def get_projet(self, obj):
        return {
            "id": obj.projet.id,
            "code": obj.projet.code,
            "name": obj.projet.name,
        }

    def get_zones_count(self, obj):
        return obj.zones.count()


class CampaignDetailSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le détail d'une campagne.
    Inclut toutes les informations demandées.
    """

    projet = ProjectSummarySerializer(read_only=True)
    zones = ZoneSummarySerializer(many=True, read_only=True)
    regions = serializers.SerializerMethodField()
    calendrier = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            "id",
            "code_campagne",
            "nom",
            "description",
            "projet",
            "zones",
            "regions",
            "calendrier",
            "date_debut",
            "date_fin",
            "created_by",
            "created_at",
            "updated_at",
        ]

    def get_regions(self, obj):
        regions = obj.zones.values_list("region", flat=True).distinct()
        return list(regions)

    def get_calendrier(self, obj):
        return {
            "date_debut": obj.date_debut,
            "date_fin": obj.date_fin,
            "duree_jours": (obj.date_fin - obj.date_debut).days if obj.date_fin and obj.date_debut else 0,
        }

    def get_created_by(self, obj):
        return {
            "id": obj.created_by.id,
            "email": obj.created_by.email,
            "full_name": obj.created_by.full_name,
            "role": obj.created_by.role,
        }


class CampaignCreateSerializer(serializers.Serializer):
    """
    Sérialiseur pour la création d'une campagne.
    Le frontend n'envoie que : projet_id, nom, description, zone_ids, date_debut, date_fin
    """

    projet_id = serializers.UUIDField()
    nom = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    zone_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
    )
    date_debut = serializers.DateField()
    date_fin = serializers.DateField()

    def validate_nom(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Le nom de la campagne est obligatoire.")
        return value

    def validate(self, attrs):
        date_debut = attrs.get("date_debut")
        date_fin = attrs.get("date_fin")
        if date_debut and date_fin and date_fin <= date_debut:
            raise serializers.ValidationError({
                "date_fin": "La date de fin doit être postérieure à la date de début."
            })
        return attrs


class CampaignUpdateSerializer(serializers.Serializer):
    """
    Sérialiseur pour la mise à jour d'une campagne.
    Champs modifiables : nom, description, zone_ids, dates
    Non modifiables : code_campagne, organization, created_by, projet
    """

    nom = serializers.CharField(max_length=200, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    zone_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
    )
    date_debut = serializers.DateField(required=False)
    date_fin = serializers.DateField(required=False)

    def validate_nom(self, value):
        if value is not None and (not value or not value.strip()):
            raise serializers.ValidationError("Le nom de la campagne ne peut pas être vide.")
        return value

    def validate(self, attrs):
        date_debut = attrs.get("date_debut")
        date_fin = attrs.get("date_fin")

        if date_debut and date_fin and date_fin <= date_debut:
            raise serializers.ValidationError({
                "date_fin": "La date de fin doit être postérieure à la date de début."
            })

        return attrs