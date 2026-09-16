from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema

from apps.projects.models import Project
from apps.zones.models import Zone
from .models import Campaign
from .serializers import (
    CampaignListSerializer,
    CampaignDetailSerializer,
    CampaignCreateSerializer,
    CampaignUpdateSerializer,
)
from .permissions import (
    IsChefProjetOrGerant,
    IsChefProjetOnly,
    CanManageCampaign,
)
from .services import (
    create_campaign,
    validate_zones_for_organization,
    validate_dates,
    validate_project_for_chef_projet,
)


@extend_schema(tags=["Campagnes"])
class CampaignListCreateView(APIView):
    """
    GET /api/campaigns/ - Liste des campagnes de l'ONG
    POST /api/campaigns/ - Création d'une campagne (CHEF_PROJET uniquement)
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsChefProjetOnly()]
        return [IsAuthenticated(), IsChefProjetOrGerant()]

    @extend_schema(
        responses={200: CampaignListSerializer(many=True)},
    )
    def get(self, request):
        """Liste les campagnes de l'ONG de l'utilisateur connecté."""
        campaigns = Campaign.objects.select_related(
            "projet", "created_by"
        ).prefetch_related(
            "zones"
        ).order_by("-created_at")

        if request.user.role != "SUPER_ADMIN":
            campaigns = campaigns.filter(organization=request.user.organization)
        if request.user.role == "AGENT":
            campaigns = campaigns.filter(affectations__agent=request.user).distinct()

        serializer = CampaignListSerializer(campaigns, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=CampaignCreateSerializer,
        responses={201: CampaignDetailSerializer},
    )
    def post(self, request):
        """
        Crée une nouvelle campagne.

        Vérifications effectuées :
         Authentification JWT
         Rôle = CHEF_PROJET
         Projet existe, appartient à la même ONG, chef de projet affecté
         Zones existent, appartiennent à la même ONG, au moins une zone
        date_fin > date_debut
        """
        serializer = CampaignCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            campaign = create_campaign(serializer.validated_data, request.user)
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        detail_serializer = CampaignDetailSerializer(campaign)
        return Response(
            {
                "id": campaign.id,
                "code_campagne": campaign.code_campagne,
                "message": "Campagne créée avec succès.",
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Campagnes"])
class CampaignDetailView(APIView):
    """
    GET /api/campaigns/{id}/ - Détail d'une campagne
    PATCH /api/campaigns/{id}/ - Modification (CHEF_PROJET uniquement)
    DELETE /api/campaigns/{id}/ - Suppression (CHEF_PROJET uniquement)
    """

    def get_object(self, pk, user):
        try:
            queryset = Campaign.objects.select_related(
                "projet", "created_by", "organization"
            ).prefetch_related(
                "zones"
            ).filter(pk=pk)
            if user.role != "SUPER_ADMIN":
                queryset = queryset.filter(organization=user.organization)
            if user.role == "AGENT":
                queryset = queryset.filter(affectations__agent=user)
            return queryset.get()
        except Campaign.DoesNotExist:
            return None

    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAuthenticated(), IsChefProjetOnly(), CanManageCampaign()]
        return [IsAuthenticated(), IsChefProjetOrGerant()]

    @extend_schema(
        responses={200: CampaignDetailSerializer},
    )
    def get(self, request, pk):
        """Retourne le détail complet d'une campagne."""
        campaign = self.get_object(pk, request.user)
        if not campaign:
            return Response(
                {"detail": "Campagne non trouvée."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CampaignDetailSerializer(campaign)
        return Response(serializer.data)

    @extend_schema(
        request=CampaignUpdateSerializer,
        responses={200: CampaignDetailSerializer},
    )
    def patch(self, request, pk):
        """
        Met à jour une campagne.
        Champs modifiables : nom, description, zone_ids, date_debut, date_fin
        Non modifiables : code_campagne, organization, created_by, projet
        """
        campaign = self.get_object(pk, request.user)
        if not campaign:
            return Response(
                {"detail": "Campagne non trouvée."},
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, campaign)

        serializer = CampaignUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        if "nom" in validated_data:
            campaign.nom = validated_data["nom"]

        if "description" in validated_data:
            campaign.description = validated_data["description"]

        if "zone_ids" in validated_data:
            zone_ids = validated_data["zone_ids"]
            try:
                zones = validate_zones_for_organization(zone_ids, request.user.organization)
                campaign.zones.set(zones)
            except ValueError as e:
                return Response(
                    {"detail": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if "date_debut" in validated_data or "date_fin" in validated_data:
            new_date_debut = validated_data.get("date_debut", campaign.date_debut)
            new_date_fin = validated_data.get("date_fin", campaign.date_fin)
            try:
                validate_dates(new_date_debut, new_date_fin)
            except ValueError as e:
                return Response(
                    {"detail": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            campaign.date_debut = new_date_debut
            campaign.date_fin = new_date_fin

        campaign.save()

        detail_serializer = CampaignDetailSerializer(campaign)
        return Response(detail_serializer.data)

    @extend_schema(
        responses={204: None},
    )
    def delete(self, request, pk):
        """Supprime une campagne (CHEF_PROJET uniquement)."""
        campaign = self.get_object(pk, request.user)
        if not campaign:
            return Response(
                {"detail": "Campagne non trouvée."},
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, campaign)

        campaign.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)