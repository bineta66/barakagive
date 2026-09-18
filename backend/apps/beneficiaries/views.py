from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema

from apps.campaigns.models import Campaign
from apps.zones.models import Zone
from apps.forms.models import Formulaire
from .models import Beneficiary, FormResponse
from .serializers import (
    BeneficiaryListSerializer,
    BeneficiaryDetailSerializer,
    BeneficiaryCreateSerializer,
    BeneficiaryUpdateSerializer,
    BeneficiarySyncSerializer,
)
from .permissions import (
    IsAgentOrChefProjetOrGerant,
    IsAgentOnly,
    CanManageBeneficiary,
    CanViewBeneficiary,
)
from .services import (
    create_beneficiary_with_responses,
    update_beneficiary,
    sync_pending_beneficiaries,
    update_ai_score,
    build_zone_ranking,
    BeneficiaryError,
)


@extend_schema(tags=["Bénéficiaires"])
class BeneficiaryListCreateView(APIView):
    """
    GET /api/beneficiaries/ - Liste des bénéficiaires
    POST /api/beneficiaries/ - Créer un bénéficiaire + réponses (AGENT)
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAgentOnly()]
        return [IsAuthenticated(), IsAgentOrChefProjetOrGerant()]

    @extend_schema(
        responses={200: BeneficiaryListSerializer(many=True)},
    )
    def get(self, request):
        """
        Liste les bénéficiaires selon le rôle :
        - AGENT : ses propres bénéficiaires
        - CHEF_PROJET : bénéficiaires de ses campagnes
        - GERANT : tous les bénéficiaires de son ONG
        """
        if request.user.role == "AGENT":
            beneficiaries = Beneficiary.objects.filter(
                created_by=request.user,
                organization=request.user.organization,
            ).select_related(
                "campagne", "zone", "created_by"
            ).order_by("-created_at")

        elif request.user.role == "CHEF_PROJET":
            beneficiaries = Beneficiary.objects.filter(
                campagne__projet__chef_projet=request.user,
                organization=request.user.organization,
            ).select_related(
                "campagne", "zone", "created_by"
            ).order_by("-created_at")

            beneficiaries |= Beneficiary.objects.filter(
                created_by=request.user,
                organization=request.user.organization,
            ).select_related(
                "campagne", "zone", "created_by"
            ).order_by("-created_at")

        else:  # GERANT
            beneficiaries = Beneficiary.objects.filter(
                organization=request.user.organization,
            ).select_related(
                "campagne", "zone", "created_by"
            ).order_by("-created_at")

        serializer = BeneficiaryListSerializer(beneficiaries, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=BeneficiaryCreateSerializer,
        responses={201: BeneficiaryDetailSerializer},
    )
    def post(self, request):
        """
        Crée un bénéficiaire avec ses réponses en un seul appel.
        Le backend sépare automatiquement :
        - Informations personnelles → table Beneficiary
        - Réponses → table FormResponse

        Vérifications :
        1. JWT valide
        2. Rôle = AGENT
        3. Campagne, zone, formulaire existent
        4. Zone appartient à la campagne
        5. Formulaire publié et appartient à la campagne
        6. Pas de doublon dans la campagne (téléphone ou nom+prénom+date)
        7. Pas de doublon de synchronisation (local_id + device_id)
        """
        serializer = BeneficiaryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            beneficiary, responses, is_duplicate = create_beneficiary_with_responses(
                serializer.validated_data, request.user
            )
        except BeneficiaryError as e:
            if "déjà inscrit" in str(e):
                return Response(
                    {"detail": str(e)},
                    status=status.HTTP_409_CONFLICT
                )
            elif "déjà été synchronisé" in str(e):
                return Response(
                    {"detail": str(e)},
                    status=status.HTTP_409_CONFLICT
                )
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        detail_serializer = BeneficiaryDetailSerializer(beneficiary)
        return Response(
            {
                "id": beneficiary.id,
                "nom": beneficiary.nom,
                "prenom": beneficiary.prenom,
                "telephone": beneficiary.telephone,
                "message": "Bénéficiaire créé avec succès.",
                "responses_count": len(responses),
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Bénéficiaires"])
class BeneficiaryDetailView(APIView):
    """
    GET /api/beneficiaries/{id}/ - Détail + réponses
    PATCH /api/beneficiaries/{id}/ - Modifier infos personnelles
    DELETE /api/beneficiaries/{id}/ - Supprimer bénéficiaire + réponses
    """

    def get_object(self, pk, user):
        try:
            return Beneficiary.objects.select_related(
                "campagne", "campagne__projet", "zone", "created_by", "organization"
            ).prefetch_related(
                "responses__question", "responses__formulaire"
            ).get(pk=pk, organization=user.organization)
        except Beneficiary.DoesNotExist:
            return None

    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAuthenticated(), CanManageBeneficiary()]
        return [IsAuthenticated(), IsAgentOrChefProjetOrGerant(), CanViewBeneficiary()]

    @extend_schema(
        responses={200: BeneficiaryDetailSerializer},
    )
    def get(self, request, pk):
        """Retourne le détail complet du bénéficiaire avec ses réponses."""
        beneficiary = self.get_object(pk, request.user)
        if not beneficiary:
            return Response(
                {"detail": "Bénéficiaire non trouvé."},
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, beneficiary)

        serializer = BeneficiaryDetailSerializer(beneficiary)
        return Response(serializer.data)

    @extend_schema(
        request=BeneficiaryUpdateSerializer,
        responses={200: BeneficiaryDetailSerializer},
    )
    def patch(self, request, pk):
        """Met à jour les informations personnelles d'un bénéficiaire."""
        beneficiary = self.get_object(pk, request.user)
        if not beneficiary:
            return Response(
                {"detail": "Bénéficiaire non trouvé."},
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, beneficiary)

        serializer = BeneficiaryUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            beneficiary = update_beneficiary(beneficiary, serializer.validated_data, request.user)
        except BeneficiaryError as e:
            if "existe déjà" in str(e):
                return Response(
                    {"detail": str(e)},
                    status=status.HTTP_409_CONFLICT
                )
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        detail_serializer = BeneficiaryDetailSerializer(beneficiary)
        return Response(detail_serializer.data)

    @extend_schema(
        responses={204: None},
    )
    def delete(self, request, pk):
        """Supprime un bénéficiaire et toutes ses réponses."""
        beneficiary = self.get_object(pk, request.user)
        if not beneficiary:
            return Response(
                {"detail": "Bénéficiaire non trouvé."},
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, beneficiary)

        beneficiary.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["Bénéficiaires"])
class BeneficiarySyncView(APIView):
    """
    POST /api/beneficiaries/sync/ - Synchroniser les bénéficiaires en attente (mode hors ligne)
    """

    permission_classes = [IsAuthenticated, IsAgentOnly]

    @extend_schema(
        request=BeneficiaryCreateSerializer(many=True),
        responses={200: BeneficiarySyncSerializer},
    )
    def post(self, request):
        """
        Synchronise une liste de bénéficiaires créés hors ligne.
        Chaque bénéficiaire est traité dans sa propre transaction.
        Les doublons n'empêchent pas la synchronisation des autres.

        Body :
        [
          { ... données bénéficiaire 1 ... },
          { ... données bénéficiaire 2 ... },
          ...
        ]

        Réponse :
        {
          "synced": 2,
          "duplicates": 1,
          "failed": 0,
          "details": [...]
        }
        """
        if not isinstance(request.data, list):
            return Response(
                {"detail": "Le corps de la requête doit être une liste de bénéficiaires."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not request.data:
            return Response(
                {"detail": "Aucun bénéficiaire à synchroniser."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Valider chaque entrée
        for item in request.data:
            serializer = BeneficiaryCreateSerializer(data=item)
            serializer.is_valid(raise_exception=True)

        result = sync_pending_beneficiaries(request.data, request.user)

        return Response(result)


@extend_schema(tags=["Bénéficiaires"])
class BeneficiaryAIScoreView(APIView):
    """
    POST /api/beneficiaries/{id}/ai-score/ - Calculer/mettre à jour le score IA
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Beneficiary.objects.select_related(
                "campagne", "campagne__projet", "organization"
            ).get(pk=pk, organization=user.organization)
        except Beneficiary.DoesNotExist:
            return None

    def post(self, request, pk):
        """Calcule et met à jour le score IA du bénéficiaire."""
        beneficiary = self.get_object(pk, request.user)
        if not beneficiary:
            return Response(
                {"detail": "Bénéficiaire non trouvé."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Vérifier les permissions
        if request.user.role == "AGENT" and beneficiary.created_by != request.user:
            return Response(
                {"detail": "Vous ne pouvez calculer le score que de vos propres bénéficiaires."},
                status=status.HTTP_403_FORBIDDEN
            )

        if request.user.role == "CHEF_PROJET" and beneficiary.campagne.projet.chef_projet != request.user:
            return Response(
                {"detail": "Ce bénéficiaire n'appartient pas à vos campagnes."},
                status=status.HTTP_403_FORBIDDEN
            )

        if beneficiary.organization != request.user.organization:
            return Response(
                {"detail": "Ce bénéficiaire n'appartient pas à votre ONG."},
                status=status.HTTP_403_FORBIDDEN
            )

        beneficiary = update_ai_score(beneficiary)

        return Response({
            "id": beneficiary.id,
            "ai_score": str(beneficiary.ai_score),
            "message": "Score IA mis à jour.",
        })


@extend_schema(tags=["Bénéficiaires"])
class ZoneRankingView(APIView):
    """
    GET /api/beneficiaries/zone-ranking/?campaign_id=<uuid>
    Retourne le classement des zones d'une campagne :
    - score_total
    - beneficiaires_prioritaires
    - top5 bénéficiaires par zone avec score + raisons
    """

    permission_classes = [IsAuthenticated, IsAgentOrChefProjetOrGerant]

    def get(self, request):
        campaign_id = request.query_params.get("campaign_id")
        if not campaign_id:
            return Response(
                {"detail": "Le paramètre campaign_id est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            campaign = Campaign.objects.select_related("organization").get(id=campaign_id)
        except Campaign.DoesNotExist:
            return Response(
                {"detail": "Campagne non trouvée."},
                status=status.HTTP_404_NOT_FOUND
            )

        if campaign.organization != request.user.organization:
            return Response(
                {"detail": "Cette campagne n'appartient pas à votre ONG."},
                status=status.HTTP_403_FORBIDDEN
            )

        ranking = build_zone_ranking(campaign)
        return Response(ranking)
