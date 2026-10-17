from rest_framework import serializers
from apps.common.validators import validate_description

from apps.projects.models import Project
from apps.zones.models import Zone
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

    agent_id = serializers.IntegerField()
    zone = serializers.CharField(max_length=150, required=False, allow_blank=True)
    zones = serializers.ListField(
        child=serializers.CharField(max_length=150),
        required=False,
        default=list,
    )
    objectif = serializers.IntegerField(min_value=0, default=0)

    def validate(self, attrs):
        zones = [z.strip() for z in attrs.get("zones", []) if str(z).strip()]
        legacy = (attrs.get("zone") or "").strip()
        if legacy and legacy not in zones:
            zones.insert(0, legacy)
        attrs["zones"] = zones
        return attrs


class AgentCampagneSerializer(serializers.ModelSerializer):
    """Vue minimale d'une campagne pour l'agent connecté."""

    projet = serializers.CharField(source="projet.name", read_only=True)
    image = serializers.SerializerMethodField()
    zone = serializers.SerializerMethodField()
    zones = serializers.SerializerMethodField()
    objectif = serializers.SerializerMethodField()
    objectif_total = serializers.SerializerMethodField()
    collectes = serializers.IntegerField(read_only=True)
    statut = serializers.CharField(read_only=True)

    class Meta:
        model = Campaign
        fields = [
            "id", "nom", "projet", "image", "date_debut", "date_fin",
            "zone", "zones", "objectif", "objectif_total", "collectes", "statut", "type",
        ]

    def _assignments(self, obj):
        """Affectations de l'agent pour cette campagne (une par zone)."""
        agent = self.context.get("agent")
        queryset = obj.affectations.all()
        if agent is not None:
            queryset = queryset.filter(agent=agent)
        return list(queryset)

    def get_image(self, obj):
        return None
    def get_zones(self, obj):
        campaign_zones = list(obj.zones.filter(organization_id=obj.organization_id))
        assignments = self._assignments(obj)
        assigned_names = [a.zone for a in assignments if a.zone]

        if self.context.get("agent") is not None:
            allowed_names = set(assigned_names)
            return [
                {
                    "id": str(z.id),
                    "nom": z.nom,
                    "latitude": str(z.latitude) if z.latitude is not None else None,
                    "longitude": str(z.longitude) if z.longitude is not None else None,
                }
                for z in campaign_zones
                if z.organization_id == obj.organization_id
                and (z.nom in allowed_names or str(z.id) in allowed_names)
            ]

        if campaign_zones:
            if assigned_names:
                filtered = [
                    z for z in campaign_zones
                    if z.organization_id == obj.organization_id
                    and (z.nom in assigned_names or str(z.id) in assigned_names)
                ]
                if filtered:
                    return [
                        {
                            "id": str(z.id),
                            "nom": z.nom,
                            "latitude": str(z.latitude) if z.latitude is not None else None,
                            "longitude": str(z.longitude) if z.longitude is not None else None,
                        }
                        for z in filtered
                    ]
            return [
                {
                    "id": str(z.id),
                    "nom": z.nom,
                    "latitude": str(z.latitude) if z.latitude is not None else None,
                    "longitude": str(z.longitude) if z.longitude is not None else None,
                }
                for z in campaign_zones
            ]

        if assigned_names:
            matched_zones = {
                z.nom: z for z in Zone.objects.filter(
                    nom__in=assigned_names, organization_id=obj.organization_id,
                )
            }
            result = []
            for name in assigned_names:
                z = matched_zones.get(name)
                result.append({
                    "id": str(z.id) if z else name,
                    "nom": name,
                    "latitude": str(z.latitude) if (z and z.latitude is not None) else None,
                    "longitude": str(z.longitude) if (z and z.longitude is not None) else None,
                })
            return result

        all_zones = Zone.objects.filter(organization=obj.organization, statut=True)
        return [
            {
                "id": str(z.id),
                "nom": z.nom,
                "latitude": str(z.latitude) if z.latitude is not None else None,
                "longitude": str(z.longitude) if z.longitude is not None else None,
            }
            for z in all_zones
        ]

    def get_zone(self, obj):
        assignments = self._assignments(obj)
        if assignments and assignments[0].zone:
            return assignments[0].zone
        if obj.zones.exists():
            return obj.zones.first().nom
        return None
    def get_objectif(self, obj):
        assignments = self._assignments(obj)
        return assignments[0].objectif_beneficiaires if assignments else 0
    def get_objectif_total(self, obj):
        return sum(a.objectif_beneficiaires for a in self._assignments(obj))


class AgentDashboardSerializer(serializers.Serializer):
    agent = serializers.CharField()
    campagnes_actives = serializers.IntegerField()
    zones_assignees = serializers.IntegerField()
    beneficiaires_enregistres = serializers.IntegerField()
    beneficiaires_prioritaires = serializers.IntegerField()
    objectif_total = serializers.IntegerField()
    progression = serializers.FloatField()


class AgentZonesAssignmentSerializer(serializers.Serializer):
    """Requete d'affectation d'un agent a une ou plusieurs zones."""

    agent_id = serializers.IntegerField()
    zones = serializers.ListField(
        child=serializers.CharField(max_length=150),
        allow_empty=False,
    )
    objectif = serializers.IntegerField(min_value=0, default=0)

class ZoneSummarySerializer(serializers.ModelSerializer):
    region_nom = serializers.CharField(source="region.nom", read_only=True)

    """Sérialiseur minimal pour les zones dans les listes."""

    class Meta:
        model = Zone
        fields = ["id", "nom", "region", "region_nom", "departement"]


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
    statut = serializers.CharField(read_only=True)

    class Meta:
        model = Campaign
        fields = [
            "id",
            "code_campagne",
            "nom",
            "projet",
            "zones_count",
            "type",
            "date_debut",
            "date_fin",
            "statut",
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
            "type",
            "projet",
            "zones",
            "regions",
            "calendrier",
            "date_debut",
            "date_fin",
            "created_by",
            "created_at",
            "updated_at",
            "statut",
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
    type = serializers.ChoiceField(
        choices=[choice for choice in Campaign.Type.choices if choice[0] != Campaign.Type.COLLECTE],
        required=False,
        default=Campaign.Type.DISTRIBUTION,
    )
    statut = serializers.ChoiceField(choices=Campaign.Statut.choices, required=False)
    agents = AgentAssignmentInputSerializer(many=True, required=False, default=list)
    def validate_zone_ids(self, value):
        """Validate zone IDs for creation, similar to update serializer."""
        if value is None:
            return value
        normalized = [str(value_id) for value_id in value]
        if len(normalized) != len(set(normalized)):
            raise serializers.ValidationError("Une zone ne peut être sélectionnée qu'une seule fois.")
        return value


    def validate_nom(self, value):
        v = (value or "").strip()
        if not v:
            raise serializers.ValidationError("Le nom de la campagne est obligatoire.")
        if len(v) < 3:
            raise serializers.ValidationError("Le nom de la campagne doit contenir au moins 3 caractères.")
        if len(v) > 200:
            raise serializers.ValidationError("Le nom de la campagne ne peut pas dépasser 200 caractères.")
        return v

    def validate_description(self, value):
        value = (value or "").strip()
        try:
            return validate_description(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc))

    def validate(self, attrs):
        if not attrs.get("projet_id") and attrs.get("projet"):
            attrs["projet_id"] = attrs["projet"]
        if not attrs.get("projet_id"):
            raise serializers.ValidationError({"projet_id": "Le projet est obligatoire."})
        date_debut = attrs.get("date_debut")
        date_fin   = attrs.get("date_fin")
        if date_debut and date_fin and date_fin < date_debut:
            raise serializers.ValidationError({
                "date_fin": "La date de fin doit être égale ou postérieure à la date de début."
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
        min_length=1,
    )
    date_debut = serializers.DateField(required=False)
    date_fin = serializers.DateField(required=False)
    type = serializers.ChoiceField(
        choices=[choice for choice in Campaign.Type.choices if choice[0] != Campaign.Type.COLLECTE],
        required=False,
    )
    statut = serializers.ChoiceField(choices=Campaign.Statut.choices, required=False)

    def validate_zone_ids(self, value):
        """Validate zone IDs for updates, same logic as creation validator."""
        if value is None:
            return value
        normalized = [str(value_id) for value_id in value]
        if len(normalized) != len(set(normalized)):
            raise serializers.ValidationError("Une zone ne peut être sélectionnée qu'une seule fois.")
        return value

    def validate_nom(self, value):
        value = (value or "").strip()
        if len(value) < 3:
            raise serializers.ValidationError("Le nom de la campagne doit contenir au moins 3 caractères.")
        if len(value) > 200:
            raise serializers.ValidationError("Le nom de la campagne ne peut pas dépasser 200 caractères.")
        return value

    def validate_description(self, value):
        value = (value or "").strip()
        try:
            return validate_description(value)
        except Exception as exc:
            raise serializers.ValidationError(str(exc))

    def validate(self, attrs):
        # Prevent modification of immutable fields
        if "projet" in attrs or "projet_id" in attrs:
            raise serializers.ValidationError({"projet": "Le projet ne peut pas être modifié via la mise à jour."})
        instance = self.instance
        date_debut = attrs.get("date_debut", getattr(instance, "date_debut", None))
        date_fin = attrs.get("date_fin", getattr(instance, "date_fin", None))

        if date_debut and date_fin and date_fin < date_debut:
            raise serializers.ValidationError({
                "date_fin": "La date de fin doit être égale ou postérieure à la date de début."
            })

        return attrs
