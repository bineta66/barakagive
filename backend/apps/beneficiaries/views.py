import logging
from django.db.models import Exists, OuterRef, F, Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)

from drf_spectacular.utils import extend_schema

from apps.campaigns.models import Campaign
from apps.zones.models import Zone
from apps.common.pagination import StandardPagination
from apps.accounts.permissions import IsAccountActive
from .models import Beneficiary, HumanitarianAction
from .serializers import (
    BeneficiaryListSerializer,
    BeneficiaryDetailSerializer,
    BeneficiaryCreateSerializer,
    BeneficiaryUpdateSerializer,
    BeneficiarySyncSerializer,
    HumanitarianActionSerializer,
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
    update_vulnerability_score,
    build_zone_ranking,
    build_region_priorities,
    build_all_regions_scores,
    region_exists_in_project,
    get_zone_beneficiaries_table_data,
    BeneficiaryError,
)


@extend_schema(tags=["Bénéficiaires"])
class BeneficiaryListCreateView(APIView):
    """
    GET /api/beneficiaries/ - Liste des bénéficiaires
    POST /api/beneficiaries/ - Créer un bénéficiaire + réponses (AGENT)
    """

    def get_permissions(self):
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
        if not request.user.organization_id:
            beneficiaries = Beneficiary.objects.none()
        elif request.user.role == "AGENT":
            from apps.campaigns.models import CampagneAffectation
            assigned_campaign_zone = CampagneAffectation.objects.filter(
                campagne_id=OuterRef("campagne_id"),
                agent=request.user,
                zone=OuterRef("zone__nom"),
            )
            beneficiaries = Beneficiary.objects.filter(
                created_by=request.user,
                organization=request.user.organization,
                campagne__organization=request.user.organization,
                campagne__projet__organization=request.user.organization,
                zone__organization=request.user.organization,
            ).filter(
                Exists(assigned_campaign_zone),
            ).select_related(
                "campagne", "zone", "created_by"
            ).order_by("-created_at")

        elif request.user.role == "CHEF_PROJET":
            beneficiaries = Beneficiary.objects.filter(
                campagne__projet__chef_projet=request.user,
                organization=request.user.organization,
                campagne__organization=request.user.organization,
                zone__organization=request.user.organization,
            ).select_related(
                "campagne", "zone", "created_by"
            ).order_by("-created_at")

            beneficiaries |= Beneficiary.objects.filter(
                created_by=request.user,
                organization=request.user.organization,
                campagne__organization=request.user.organization,
                campagne__projet__organization=request.user.organization,
                zone__organization=request.user.organization,
            ).select_related(
                "campagne", "zone", "created_by"
            ).order_by("-created_at")

        else:  # GERANT
            beneficiaries = Beneficiary.objects.filter(
                organization=request.user.organization,
                campagne__organization=request.user.organization,
                campagne__projet__organization=request.user.organization,
                zone__organization=request.user.organization,
            ).select_related(
                "campagne", "zone", "created_by"
            ).order_by("-created_at")

        zone_id = request.query_params.get("zone") or request.query_params.get("zone_id")
        if zone_id:
            beneficiaries = beneficiaries.filter(zone_id=zone_id)
        region = (request.query_params.get("region") or "").strip()
        if region:
            beneficiaries = beneficiaries.filter(zone__region__nom__iexact=region)

        campaign_id = request.query_params.get("campagne") or request.query_params.get("campaign_id")
        if campaign_id:
            beneficiaries = beneficiaries.filter(campagne_id=campaign_id)
        vulnerability_status = request.query_params.get("statut")
        if vulnerability_status == "Critique":
            beneficiaries = beneficiaries.filter(score_vulnerabilite__gte=80)
        elif vulnerability_status == "Élevé":
            beneficiaries = beneficiaries.filter(score_vulnerabilite__gte=50, score_vulnerabilite__lt=80)
        elif vulnerability_status == "Normal":
            beneficiaries = beneficiaries.filter(score_vulnerabilite__lt=50)
        elif vulnerability_status == "Non évalué":
            beneficiaries = beneficiaries.filter(score_vulnerabilite__isnull=True)

        search = (request.query_params.get("search") or "").strip()
        if search:
            beneficiaries = beneficiaries.filter(
                Q(nom__icontains=search)
                | Q(prenom__icontains=search)
                | Q(telephone__icontains=search)
            )

        paginator = StandardPagination()
        page = paginator.paginate_queryset(beneficiaries, request, view=self)
        serializer = BeneficiaryListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

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
            ).get(
                pk=pk,
                organization=user.organization,
                campagne__organization=user.organization,
                campagne__projet__organization=user.organization,
                zone__organization=user.organization,
            )
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
        validated_items = []
        for item in request.data:
            serializer = BeneficiaryCreateSerializer(data=item)
            serializer.is_valid(raise_exception=True)
            validated_items.append(serializer.validated_data)

        result = sync_pending_beneficiaries(validated_items, request.user)

        return Response(result)


@extend_schema(tags=["Bénéficiaires"])
class BeneficiaryPWASyncView(APIView):
    """
    POST /api/beneficiaries/pwa-sync/
    Synchronisation unitaire ou par lot pour la PWA / mode hors-ligne.
    Accepte :
    - Soit un dictionnaire unique : { local_id, campagne_id, zone_id, formulaire_id, beneficiary, responses }
    - Soit une liste de dictionnaires : [ { ... }, { ... } ]

    Chaque élément est traité indépendamment dans sa propre transaction.
    Un doublon ou une erreur de validation sur un élément NE BLOQUE JAMAIS les autres.
    Retourne toujours les détails précis de chaque refus/doublon.
    """
    permission_classes = [IsAuthenticated, IsAgentOrChefProjetOrGerant]

    def _sync_single_item(self, data, user):
        if not isinstance(data, dict):
            return {
                "success": False,
                "status_code": status.HTTP_400_BAD_REQUEST,
                "data": {
                    "local_id": None,
                    "status": "FAILED",
                    "detail": "Chaque élément doit être un objet JSON.",
                },
            }

        # Valider et normaliser avant toute requête utilisant un identifiant client.
        serializer = BeneficiaryCreateSerializer(data=data)
        if not serializer.is_valid():
            local_id = data.get("local_id")
            error_msgs = []
            for field, errs in serializer.errors.items():
                if isinstance(errs, dict):
                    sub_errs = [f"{k}: {', '.join(v) if isinstance(v, list) else v}" for k, v in errs.items()]
                    error_msgs.append("; ".join(sub_errs))
                elif isinstance(errs, list):
                    error_msgs.append(f"{field}: {', '.join(str(err) for err in errs)}")
                else:
                    error_msgs.append(f"{field}: {errs}")
            return {
                "success": False,
                "status_code": status.HTTP_400_BAD_REQUEST,
                "data": {
                    "local_id": str(local_id) if local_id else None,
                    "status": "FAILED",
                    "detail": " | ".join(error_msgs) or "Données de formulaire invalides.",
                    "errors": serializer.errors,
                },
            }

        validated_data = serializer.validated_data
        local_id = validated_data.get("local_id")

        # Idempotency lookup uses the UUID only after serializer validation.
        if local_id:
            existing = Beneficiary.objects.filter(
                local_id=local_id,
                organization_id=user.organization_id,
                campagne__organization_id=user.organization_id,
                campagne__projet__organization_id=user.organization_id,
                zone__organization_id=user.organization_id,
                created_by__organization_id=user.organization_id,
            ).first()
            if existing:
                return {
                    "success": True,
                    "status_code": status.HTTP_200_OK,
                    "data": {
                        "id": str(existing.id),
                        "local_id": str(existing.local_id),
                        "nom": existing.nom,
                        "prenom": existing.prenom,
                        "status": "SYNCED",
                        "message": "Bénéficiaire déjà synchronisé précédemment.",
                    }
                }

        # 3. Création avec transaction atomique individuelle
        try:
            beneficiary, responses, is_duplicate = create_beneficiary_with_responses(
                validated_data, user
            )
            return {
                "success": True,
                "status_code": status.HTTP_201_CREATED,
                "data": {
                    "id": str(beneficiary.id),
                    "local_id": str(beneficiary.local_id),
                    "nom": beneficiary.nom,
                    "prenom": beneficiary.prenom,
                    "telephone": beneficiary.telephone,
                    "status": "SYNCED",
                    "message": "Bénéficiaire synchronisé avec succès.",
                    "responses_count": len(responses),
                }
            }
        except BeneficiaryError as e:
            err_text = str(e)
            is_dup = "déjà inscrit" in err_text or "doublon" in err_text.lower() or "existe déjà" in err_text.lower()
            return {
                "success": False,
                "status_code": status.HTTP_409_CONFLICT if is_dup else status.HTTP_400_BAD_REQUEST,
                "data": {
                    "local_id": str(local_id) if local_id else None,
                    "status": "CONFLICT" if is_dup else "FAILED",
                    "detail": err_text,
                    "code": "DUPLICATE" if is_dup else "VALIDATION_ERROR",
                }
            }
        except Exception as e:
            logger.error(f"Unexpected error in _sync_single_item: {e}", exc_info=True)
            return {
                "success": False,
                "status_code": status.HTTP_400_BAD_REQUEST,
                "data": {
                    "local_id": str(local_id) if local_id else None,
                    "status": "FAILED",
                    "detail": "Erreur interne lors du traitement de cet élément.",
                }
            }

    def post(self, request):
        # Cas 1 : Envoi groupé (liste)
        if isinstance(request.data, list):
            if not request.data:
                return Response(
                    {"detail": "Aucun bénéficiaire à synchroniser."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            synced = 0
            conflict = 0
            failed = 0
            details = []
            for item in request.data:
                res = self._sync_single_item(item, request.user)
                details.append(res["data"])
                if res["success"]:
                    synced += 1
                elif res["status_code"] == status.HTTP_409_CONFLICT:
                    conflict += 1
                else:
                    failed += 1
            return Response({
                "synced": synced,
                "conflict": conflict,
                "failed": failed,
                "total": len(request.data),
                "details": details,
            }, status=status.HTTP_200_OK)

        # Cas 2 : Envoi unitaire (dictionnaire)
        res = self._sync_single_item(request.data, request.user)
        return Response(res["data"], status=res["status_code"])


@extend_schema(tags=["Bénéficiaires"])
class BeneficiaryVulnerabilityScoreView(APIView):
    """
    POST /api/beneficiaries/{id}/vulnerability-score/ - Recalculer le score métier.

    The historical ``ai-score`` route remains registered for API compatibility.
    """

    permission_classes = [IsAuthenticated, IsAccountActive]

    def get_object(self, pk, user):
        try:
            return Beneficiary.objects.select_related(
                "campagne", "campagne__projet", "zone", "organization"
            ).get(pk=pk, organization=user.organization)
        except Beneficiary.DoesNotExist:
            return None

    def post(self, request, pk):
        """Calcule et met à jour le score de vulnérabilité déterministe."""
        if request.user.role not in {"AGENT", "CHEF_PROJET", "GERANT"}:
            return Response({"detail": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)
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

        if request.user.role == "AGENT":
            from apps.campaigns.models import CampagneAffectation
            if not CampagneAffectation.objects.filter(
                campagne=beneficiary.campagne,
                agent=request.user,
                zone=beneficiary.zone.nom,
            ).exists():
                return Response(
                    {"detail": "Cette zone ne fait pas partie de votre affectation."},
                    status=status.HTTP_403_FORBIDDEN,
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

        beneficiary = update_vulnerability_score(beneficiary)

        return Response({
            "id": beneficiary.id,
            "score_vulnerabilite": str(beneficiary.score_vulnerabilite),
            "message": "Score de vulnérabilité mis à jour.",
        })


@extend_schema(tags=["Actions humanitaires"])
class BeneficiaryActionListCreateView(APIView):
    """Read actions in the beneficiary's scope; assigned agents can record their own."""

    def _beneficiary(self, request, pk):
        queryset = Beneficiary.objects.select_related(
            "campagne", "campagne__projet", "zone", "organization"
        ).filter(pk=pk).filter(
            Q(organization_id=F("campagne__organization_id"))
            & Q(organization_id=F("zone__organization_id"))
            & Q(campagne__projet__organization_id=F("campagne__organization_id"))
        )
        if request.user.role != "SUPER_ADMIN":
            queryset = queryset.filter(organization_id=request.user.organization_id)
        if request.user.role == "AGENT":
            queryset = queryset.filter(created_by=request.user)
            from apps.campaigns.models import CampagneAffectation
            assigned_campaign_zone = CampagneAffectation.objects.filter(
                campagne_id=OuterRef("campagne_id"),
                agent=request.user,
                zone=OuterRef("zone__nom"),
            )
            queryset = queryset.filter(Exists(assigned_campaign_zone))
        elif request.user.role == "CHEF_PROJET":
            queryset = queryset.filter(campagne__projet__chef_projet=request.user)
        elif request.user.role not in {"GERANT", "SUPER_ADMIN"}:
            return None
        return queryset.first()

    def get(self, request, pk):
        if not request.user.is_authenticated or not request.user.can_login:
            return Response({"detail": "Authentification requise."}, status=status.HTTP_403_FORBIDDEN)
        beneficiary = self._beneficiary(request, pk)
        if beneficiary is None:
            return Response({"detail": "Bénéficiaire non trouvé."}, status=status.HTTP_404_NOT_FOUND)
        actions = HumanitarianAction.objects.filter(beneficiary=beneficiary).select_related("agent")
        return Response(HumanitarianActionSerializer(actions, many=True).data)

    def post(self, request, pk):
        if (
            not request.user.is_authenticated
            or not request.user.can_login
            or request.user.role != "AGENT"
        ):
            return Response({"detail": "Seul un agent terrain actif peut enregistrer une action."}, status=status.HTTP_403_FORBIDDEN)
        beneficiary = self._beneficiary(request, pk)
        if beneficiary is None:
            return Response({"detail": "Bénéficiaire non trouvé."}, status=status.HTTP_404_NOT_FOUND)
        serializer = HumanitarianActionSerializer(
            data=request.data,
            context={"request": request, "beneficiary": beneficiary},
        )
        serializer.is_valid(raise_exception=True)
        action = serializer.save()
        if action.statut == HumanitarianAction.Statut.REALISEE:
            beneficiary.statut = Beneficiary.Statut.PRIS_EN_CHARGE
            beneficiary.save(update_fields=["statut", "updated_at"])
        return Response(
            HumanitarianActionSerializer(action).data,
            status=status.HTTP_201_CREATED,
        )


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

        campaign_queryset = Campaign.objects.select_related("organization", "projet").filter(
            projet__organization_id=F("organization_id"),
        )
        if request.user.role != "SUPER_ADMIN":
            if not request.user.organization_id:
                campaign_queryset = campaign_queryset.none()
            else:
                campaign_queryset = campaign_queryset.filter(organization_id=request.user.organization_id)
                if request.user.role == "CHEF_PROJET":
                    campaign_queryset = campaign_queryset.filter(projet__chef_projet=request.user)
                elif request.user.role == "AGENT":
                    campaign_queryset = campaign_queryset.filter(affectations__agent=request.user)
                elif request.user.role == "FINANCE":
                    campaign_queryset = campaign_queryset.filter(projet__responsable_finance=request.user)
        try:
            campaign = campaign_queryset.get(id=campaign_id)
        except Campaign.DoesNotExist:
            return Response(
                {"detail": "Campagne non trouvée."},
                status=status.HTTP_404_NOT_FOUND
            )

        ranking = build_zone_ranking(campaign, user=request.user)
        return Response(ranking)


@extend_schema(tags=["Carte des Priorités"])
class ProjectRegionsView(APIView):
    """
    GET /api/projets/{project_id}/regions/
    Retourne toutes les régions avec leur score agrégé pour coloriser la carte SVG.
    Accessible uniquement au Chef de projet.
    """

    permission_classes = [IsAuthenticated, IsAccountActive]

    def get(self, request, project_id):
        from apps.projects.models import Project

        if request.user.role not in {"GERANT", "CHEF_PROJET", "SUPER_ADMIN"}:
            return Response({"detail": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)

        projects = Project.objects.select_related(
                "chef_projet", "organization"
            ).filter(pk=project_id, archived=False)
        if request.user.role != "SUPER_ADMIN":
            projects = projects.filter(organization_id=request.user.organization_id)
        if request.user.role == "CHEF_PROJET":
            projects = projects.filter(chef_projet=request.user)
        try:
            project = projects.get()
        except Project.DoesNotExist:
            return Response(
                {"detail": "Projet introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.role != "SUPER_ADMIN" and project.organization_id != request.user.organization_id:
            return Response(
                {"detail": "Ce projet n'appartient pas à votre ONG."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if request.user.role == "CHEF_PROJET" and project.chef_projet_id != request.user.pk:
            return Response(
                {"detail": "Vous n'êtes pas chef de ce projet."},
                status=status.HTTP_403_FORBIDDEN,
            )

        regions = build_all_regions_scores(project)
        return Response(regions)


@extend_schema(tags=["Carte des Priorités"])
class RegionPrioritiesView(APIView):
    """
    GET /api/projets/{project_id}/regions/{region_name}/priorites/
    Retourne le détail complet d'une région :
    - résumé automatique
    - zones classées par score moyen décroissant
    - bénéficiaires avec critères détaillés
    """

    permission_classes = [IsAuthenticated, IsAccountActive]

    def get(self, request, project_id, region_name):
        from apps.projects.models import Project

        if request.user.role not in {"GERANT", "CHEF_PROJET", "SUPER_ADMIN"}:
            return Response({"detail": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)

        projects = Project.objects.select_related(
                "chef_projet", "organization"
            ).filter(pk=project_id, archived=False)
        if request.user.role != "SUPER_ADMIN":
            projects = projects.filter(organization_id=request.user.organization_id)
        if request.user.role == "CHEF_PROJET":
            projects = projects.filter(chef_projet=request.user)
        try:
            project = projects.get()
        except Project.DoesNotExist:
            return Response(
                {"detail": "Projet introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.role != "SUPER_ADMIN" and project.organization_id != request.user.organization_id:
            return Response(
                {"detail": "Ce projet n'appartient pas à votre ONG."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if request.user.role == "CHEF_PROJET" and project.chef_projet_id != request.user.pk:
            return Response(
                {"detail": "Vous n'êtes pas chef de ce projet."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not region_exists_in_project(project, region_name):
            return Response(
                {"detail": "Cette région n'appartient pas au périmètre du projet."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = build_region_priorities(project, region_name)
        return Response(data)


@extend_schema(tags=["Bénéficiaires"])
class ZoneBeneficiariesTableView(APIView):
    """
    GET /api/beneficiaries/zone/<uuid:zone_id>/
    Retourne la liste complète des bénéficiaires de la zone avec leurs scores,
    informations personnelles et critères d'évaluation répondus.
    """
    permission_classes = [IsAuthenticated, IsAgentOrChefProjetOrGerant]

    def get(self, request, zone_id):
        if request.user.role not in {"AGENT", "CHEF_PROJET", "GERANT"}:
            return Response({"detail": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)
        try:
            data = get_zone_beneficiaries_table_data(
                zone_id,
                request.user,
                project_id=request.query_params.get("project_id"),
                params=request.query_params,
            )
            return Response(data)
        except BeneficiaryError as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"Erreur serveur : {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(tags=["Bénéficiaires"])
class CheckDuplicateBeneficiaryView(APIView):
    """
    GET /api/beneficiaries/check-duplicate/
    Vérifie si un bénéficiaire existe déjà dans la campagne (par téléphone ou nom+prénom+date).
    """
    permission_classes = [IsAuthenticated, IsAgentOnly]

    def get(self, request):
        campagne_id = request.query_params.get("campagne_id") or request.query_params.get("campagne")
        telephone = (request.query_params.get("telephone") or "").strip()
        nom = (request.query_params.get("nom") or "").strip()
        prenom = (request.query_params.get("prenom") or "").strip()
        date_naissance = request.query_params.get("date_naissance")
        zone_id = request.query_params.get("zone_id")

        if not campagne_id:
            return Response({"exists": False}, status=status.HTTP_200_OK)

        try:
            campaign = Campaign.objects.get(
                id=campagne_id,
                organization_id=request.user.organization_id,
                projet__organization_id=F("organization_id"),
                affectations__agent=request.user,
            )
            zone = Zone.objects.get(
                pk=zone_id,
                organization_id=request.user.organization_id,
                campaigns=campaign,
            )
            from apps.campaigns.models import CampagneAffectation
            if not CampagneAffectation.objects.filter(
                campagne=campaign, agent=request.user, zone=zone.nom,
            ).exists():
                return Response({"exists": False}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"exists": False}, status=status.HTTP_200_OK)

        from .services import check_duplicate_in_campaign
        duplicate = check_duplicate_in_campaign(
            campaign=campaign,
            telephone=telephone,
            nom=nom,
            prenom=prenom,
            date_naissance=date_naissance,
            zone=zone,
        )

        return Response({"exists": bool(duplicate)}, status=status.HTTP_200_OK)
