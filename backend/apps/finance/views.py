from django.db.models import Sum
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import requests

from .models import Budget, Don, Depense, Justification
from .serializers import (
    BudgetSerializer,
    DonSerializer,
    DepenseSerializer,
    JustificationSerializer,
)
from .permissions import FinancePermission
from .services import prepare_budget_analysis


# -------------------------------------------------------------------
# Filtre Organisation
# -------------------------------------------------------------------
class FinanceQuerysetMixin:
    def get_queryset(self):
        return self.queryset.filter(
            organization=self.request.user.organization
        )


# -------------------------------------------------------------------
# Dashboard
# -------------------------------------------------------------------
class FinanceDashboardView(APIView):
    permission_classes = [FinancePermission]

    def get(self, request):
        org = request.user.organization

        budget_total = (
            Budget.objects.filter(organization=org)
            .aggregate(total=Sum("montant"))["total"] or 0
        )

        dons_total = (
            Don.objects.filter(organization=org)
            .aggregate(total=Sum("montant"))["total"] or 0
        )

        depenses_total = (
            Depense.objects.filter(organization=org)
            .aggregate(total=Sum("montant"))["total"] or 0
        )

        solde = dons_total - depenses_total

        taux = 0
        if budget_total > 0:
            taux = round((depenses_total / budget_total) * 100, 2)

        return Response({
            "budget_total": budget_total,
            "dons_recus": dons_total,
            "depenses_totales": depenses_total,
            "solde": solde,
            "taux_execution": taux,
        })


# -------------------------------------------------------------------
# Budgets
# -------------------------------------------------------------------
class BudgetListCreateView(FinanceQuerysetMixin, generics.ListCreateAPIView):
    queryset = Budget.objects.select_related("projet")
    serializer_class = BudgetSerializer
    permission_classes = [FinancePermission]

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user,
        )


class BudgetDetailView(FinanceQuerysetMixin,
                       generics.RetrieveUpdateDestroyAPIView):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [FinancePermission]
    lookup_field = "id"


# -------------------------------------------------------------------
# Dons
# -------------------------------------------------------------------
class DonListCreateView(FinanceQuerysetMixin, generics.ListCreateAPIView):
    queryset = Don.objects.select_related(
        "projet", "campagne", "budget"
    )
    serializer_class = DonSerializer
    permission_classes = [FinancePermission]

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user,
        )


class DonDetailView(FinanceQuerysetMixin,
                    generics.RetrieveUpdateDestroyAPIView):
    queryset = Don.objects.all()
    serializer_class = DonSerializer
    permission_classes = [FinancePermission]
    lookup_field = "id"


# -------------------------------------------------------------------
# Dépenses
# -------------------------------------------------------------------
class DepenseListCreateView(FinanceQuerysetMixin,
                            generics.ListCreateAPIView):
    queryset = Depense.objects.select_related("projet", "campagne")
    serializer_class = DepenseSerializer
    permission_classes = [FinancePermission]

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user,
        )


class DepenseDetailView(FinanceQuerysetMixin,
                        generics.RetrieveUpdateDestroyAPIView):
    queryset = Depense.objects.all()
    serializer_class = DepenseSerializer
    permission_classes = [FinancePermission]
    lookup_field = "id"


# -------------------------------------------------------------------
# Justifications
# -------------------------------------------------------------------
class JustificationListCreateView(generics.ListCreateAPIView):
    serializer_class = JustificationSerializer
    permission_classes = [FinancePermission]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Justification.objects.filter(
            depense_id=self.kwargs["depense_id"],
            depense__organization=self.request.user.organization,
        )

    def perform_create(self, serializer):
        serializer.save(
            depense_id=self.kwargs["depense_id"],
            uploaded_by=self.request.user,
        )


class JustificationDetailView(generics.DestroyAPIView):
    serializer_class = JustificationSerializer
    permission_classes = [FinancePermission]
    lookup_field = "id"

    def get_queryset(self):
        return Justification.objects.filter(
            depense__organization=self.request.user.organization
        )


# -------------------------------------------------------------------
# Assistant IA
# -------------------------------------------------------------------
class BudgetAnalysisView(APIView):
    permission_classes = [FinancePermission]

    FASTAPI_URL = "http://ia_service:8001/api/ia/budget-analysis"

    def get(self, request, campaign_id):

        financial_data = prepare_budget_analysis(campaign_id)

        try:
            response = requests.post(
                self.FASTAPI_URL,
                json=financial_data,
                timeout=8,
            )

            response.raise_for_status()

            return Response({
                "financial_data": financial_data,
                "ia_analysis": response.json(),
            })

        except requests.RequestException:
            return Response(
                {
                    "financial_data": financial_data,
                    "ia_analysis": None,
                    "message": "Service IA indisponible",
                },
                status=status.HTTP_200_OK,
            )