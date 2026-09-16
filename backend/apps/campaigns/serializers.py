from rest_framework import serializers
from django.utils import timezone

from apps.projects.models import Project
from apps.zones.models import Zone
from apps.accounts.models import User
from .models import Campaign, CampagneAffectation


class CampagneAffectationSerializer(serializers.ModelSerializer):
    """Représentation publique d'une affectation de campagne."""

    agent = serializers.SerializerMethodField()

    class Meta:
        model = CampagneAffectation
        fields = [
            "id", "agent", "zone", "objectif_beneficiaires", "statut",
            "date_affectation", "created_by",
        ]
        read_only_fields = fields

    def get_agent(self, obj):
        return {
            "id": str(obj.agent_id),
            "full_name": obj.agent.full_name,
            "email": obj.agent.email,
        }


class AgentAssignmentInputSerializer(serializers.Serializer):
    """Données reçues lors de l'affectation d'un agent."""

    agent_id = serializers.UUIDField()
    zone = serializers.CharField(max_length=150, required=False, allow_blank=True)
    objectif = serializers.IntegerField(min_value=0, default=0)


class AgentCampagneSerializer(serializers.ModelSerializer):
    """Vue minimale d'une campagne pour l'agent connecté."""

    projet = serializers.CharField(source="projet.name", read_only=True)
    image = serializers.SerializerMethodField()
    zone = serializers.SerializerMethodField()
    objectif = serializers.SerializerMethodField()
    collectes = serializers.IntegerField(read_only=True)
    statut = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = ["id", "nom", "projet", "image", "date_fin", "zone", "objectif", "collectes", "statut"]

    def get_image(self, obj):
        return None

    def get_statut(self, obj):
        today = timezone.now().date()
        if obj.date_fin < today:
            return "TERMINE"
        if obj.date_debut > today:
            return "EN_ATTENTE"
        return "EN_COURS"

    def get_zone(self, obj):
        assignment = obj.affectations.all().first()
        return assignment.zone if assignment else None

    def get_objectif(self, obj):
        assignment = obj.affectations.all().first()
        return assignment.objectif_beneficiaires if assignment else 0


class AgentDashboardSerializer(serializers.Serializer):
    agent = serializers.CharField()
    campagnes_actives = serializers.IntegerField()
    beneficiaires_enregistres = serializers.IntegerField()
    objectif_total = serializers.IntegerField()
    progression = serializers.FloatField()


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

    projet_id = serializers.IntegerField(required=False)
    projet = serializers.IntegerField(required=False, write_only=True)
    nom = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    zone_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
    )
    date_debut = serializers.DateField()
    date_fin = serializers.DateField()
    agents = AgentAssignmentInputSerializer(many=True, required=False, default=list)

    def validate_nom(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Le nom de la campagne est obligatoire.")
        return value

    def validate(self, attrs):
        if not attrs.get("projet_id") and attrs.get("projet"):
            attrs["projet_id"] = attrs["projet"]
        if not attrs.get("projet_id"):
            raise serializers.ValidationError({"projet_id": "Le projet est obligatoire."})
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