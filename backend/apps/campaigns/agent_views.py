from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError

from apps.beneficiaries.models import Beneficiary
from apps.beneficiaries.serializers import BeneficiaryCreateSerializer, BeneficiaryDetailSerializer
from apps.beneficiaries.services import BeneficiaryError, create_beneficiary_with_responses
from apps.forms.models import Formulaire
from apps.forms.serializers import FormulaireDetailSerializer
from apps.zones.models import Zone
from apps.common.pagination import StandardPagination
from .models import Campaign, CampagneAffectation
from .serializers import AgentCampagneSerializer, AgentDashboardSerializer


class AgentOnly(IsAuthenticated):
    """Permission locale réservée aux agents terrain actifs."""

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == "AGENT" and request.user.can_login


def assigned_campaign_or_404(pk, user):
    campaign = get_object_or_404(
        Campaign.objects.select_related("projet").prefetch_related("affectations"),
        pk=pk,
    )
    if (
        campaign.organization_id != user.organization_id
        or campaign.projet.organization_id != user.organization_id
        or not campaign.affectations.filter(agent=user).exists()
    ):
        raise PermissionDenied("Vous n'êtes pas affecté à cette campagne.")
    return campaign


class AgentCampaignListView(APIView):
    permission_classes = [AgentOnly]

    def get(self, request):
        campaigns = (
            Campaign.objects.filter(
                affectations__agent=request.user,
                organization_id=request.user.organization_id,
                projet__organization_id=request.user.organization_id,
            )
            .select_related("projet")
            .prefetch_related("affectations")
            .annotate(
                collectes=Count(
                    "beneficiaries",
                    filter=Q(
                        beneficiaries__created_by=request.user,
                        beneficiaries__organization_id=request.user.organization_id,
                        beneficiaries__zone__organization_id=request.user.organization_id,
                    ),
                    distinct=True,
                )
            )
            .distinct()
        )
        search = (request.query_params.get("search") or "").strip()
        if search:
            campaigns = campaigns.filter(
                Q(nom__icontains=search)
                | Q(code_campagne__icontains=search)
                | Q(projet__name__icontains=search)
            )
        paginator = StandardPagination()
        page = paginator.paginate_queryset(campaigns, request, view=self)
        context = {"agent": request.user}
        return paginator.get_paginated_response(
            AgentCampagneSerializer(page, many=True, context=context).data
        )


class AgentDashboardView(APIView):
    permission_classes = [AgentOnly]

    def get(self, request):
        today = timezone.now().date()
        assignments = CampagneAffectation.objects.filter(
            agent=request.user,
            campagne__organization_id=request.user.organization_id,
            campagne__projet__organization_id=request.user.organization_id,
            campagne__date_debut__lte=today,
            campagne__date_fin__gte=today,
            campagne__statut=Campaign.Statut.EN_COURS,
        )
        beneficiaries = Beneficiary.objects.filter(
            created_by=request.user,
            campagne__affectations__agent=request.user,
            organization_id=request.user.organization_id,
            campagne__organization_id=request.user.organization_id,
            campagne__projet__organization_id=request.user.organization_id,
            zone__organization_id=request.user.organization_id,
        ).distinct()
        assigned_zones = CampagneAffectation.objects.filter(
            agent=request.user,
            campagne__organization_id=request.user.organization_id,
            campagne__projet__organization_id=request.user.organization_id,
            campagne__date_debut__lte=today,
            campagne__date_fin__gte=today,
            campagne__statut=Campaign.Statut.EN_COURS,
        )
        objectif_total = assignments.aggregate(total=Sum("objectif_beneficiaires"))["total"] or 0
        count = beneficiaries.count()
        data = {
            "agent": request.user.full_name,
            "campagnes_actives": assignments.values("campagne_id").distinct().count(),
            "zones_assignees": assigned_zones.values("zone").distinct().count(),
            "beneficiaires_enregistres": count,
            "beneficiaires_prioritaires": beneficiaries.filter(
                statut=Beneficiary.Statut.PRIORITAIRE
            ).count(),
            "objectif_total": objectif_total,
            "progression": round((count / objectif_total) * 100, 1) if objectif_total else 0.0,
        }
        return Response(AgentDashboardSerializer(data).data)


class AgentZoneListView(APIView):
    permission_classes = [AgentOnly]

    def get(self, request):
        assignments = CampagneAffectation.objects.filter(
            agent=request.user,
            campagne__organization_id=request.user.organization_id,
            campagne__projet__organization_id=request.user.organization_id,
        ).select_related("campagne", "campagne__projet")
        results = []
        for assignment in assignments:
            zone = Zone.objects.filter(
                organization_id=request.user.organization_id,
                nom=assignment.zone,
            ).first()
            if zone is None:
                try:
                    zone = Zone.objects.get(pk=assignment.zone, organization_id=request.user.organization_id)
                except (Zone.DoesNotExist, ValueError, DjangoValidationError):
                    zone = None
            if zone is not None and not assignment.campagne.zones.filter(pk=zone.pk).exists():
                zone = None
            if zone is None:
                continue
            collected = Beneficiary.objects.filter(
                created_by=request.user,
                organization_id=request.user.organization_id,
                campagne=assignment.campagne,
                zone=zone,
            ).count()
            results.append({
                "id": str(zone.pk),
                "nom": zone.nom,
                "campagne_id": str(assignment.campagne_id),
                "campagne": assignment.campagne.nom,
                "projet": assignment.campagne.projet.name,
                "beneficiaires": collected,
                "objectif": assignment.objectif_beneficiaires,
                "restant": max(0, assignment.objectif_beneficiaires - collected),
            })
        return Response(results)


class AgentCampaignFormView(APIView):
    permission_classes = [AgentOnly]

    def get(self, request, pk):
        campaign = assigned_campaign_or_404(pk, request.user)
        formulaire = (
            Formulaire.objects.filter(
                campagne=campaign,
                statut=Formulaire.Statut.PUBLIE,
            )
            .prefetch_related("fields")
            .first()
        )
        if not formulaire:
            return Response(
                {"detail": "Aucun formulaire publié pour cette campagne."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(FormulaireDetailSerializer(formulaire).data)


class AgentCampaignBeneficiaryCreateView(APIView):
    permission_classes = [AgentOnly]

    def get(self, request, pk):
        campaign = assigned_campaign_or_404(pk, request.user)
        beneficiaries = Beneficiary.objects.filter(
            campagne=campaign,
            created_by=request.user,
            organization_id=request.user.organization_id,
            campagne__organization_id=request.user.organization_id,
            campagne__projet__organization_id=request.user.organization_id,
            zone__organization_id=request.user.organization_id,
        ).select_related("zone", "campagne").order_by("-created_at")
        return Response(BeneficiaryDetailSerializer(beneficiaries, many=True).data)

    def post(self, request, pk):
        campaign = assigned_campaign_or_404(pk, request.user)
        data = request.data.copy()
        data["campagne_id"] = str(pk)
        if not data.get("zone_id"):
            # Un agent peut etre affecte a plusieurs zones : on retient la
            # premiere affectation comme zone par defaut.
            assigned_zone_names = list(
                campaign.affectations.filter(agent=request.user)
                .values_list("zone", flat=True)
            )
            if assigned_zone_names:
                zone = Zone.objects.filter(
                    organization=request.user.organization,
                    nom=assigned_zone_names[0],
                ).first()
                if zone:
                    data["zone_id"] = str(zone.id)
        serializer = BeneficiaryCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        try:
            beneficiary, responses, _ = create_beneficiary_with_responses(
                serializer.validated_data,
                request.user,
            )
        except BeneficiaryError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(BeneficiaryDetailSerializer(beneficiary).data, status=status.HTTP_201_CREATED)


class AgentSynchronizationView(APIView):
    permission_classes = [AgentOnly]

    def get(self, request):
        pending = Beneficiary.objects.filter(
            created_by=request.user,
            organization_id=request.user.organization_id,
            campagne__organization_id=request.user.organization_id,
            campagne__projet__organization_id=request.user.organization_id,
            zone__organization_id=request.user.organization_id,
            sync_status=Beneficiary.SyncStatus.PENDING,
        ).count()
        campaigns = AgentCampaignListView().get(request).data
        last_sync = Beneficiary.objects.filter(
            created_by=request.user,
            organization_id=request.user.organization_id,
            campagne__organization_id=request.user.organization_id,
            campagne__projet__organization_id=request.user.organization_id,
            zone__organization_id=request.user.organization_id,
        ).order_by("-updated_at").values_list("updated_at", flat=True).first()
        return Response({
            "last_sync": last_sync,
            "pending": pending,
            "campagnes": campaigns,
        })

    def post(self, request):
        if isinstance(request.data, list):
            records = request.data
        elif isinstance(request.data, dict) and isinstance(request.data.get("beneficiaires"), list):
            records = request.data["beneficiaires"]
        else:
            return Response(
                {"detail": "Le corps doit être une liste ou un objet contenant une liste 'beneficiaires'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not records:
            return Response(
                {"detail": "Aucun bénéficiaire à synchroniser."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        synced = []
        errors = []
        for record in records:
            serializer = BeneficiaryCreateSerializer(data=record)
            if not serializer.is_valid():
                errors.append(serializer.errors)
                continue
            try:
                beneficiary, _, _ = create_beneficiary_with_responses(serializer.validated_data, request.user)
                synced.append(str(beneficiary.id))
            except BeneficiaryError as exc:
                errors.append({"detail": str(exc)})
        return Response({"synced": synced, "errors": errors}, status=status.HTTP_200_OK)
