from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum

from .models import Budget, Don, Depense, Justification
from .permissions import FinancePermission
from .serializers import BudgetSerializer, DonSerializer, DepenseSerializer, JustificationSerializer
from .services import prepare_budget_analysis


class FinanceQuerysetMixin:
    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.filter(organization=user.organization)
        
        # Responsable Finance voit uniquement ses projets assignés
        if user.role == "FINANCE":
            # Filtrer par projets assignés (à adapter selon votre logique d'assignation)
            # Pour l'instant, on suppose que le FINANCE voit tout de son organisation
            pass
        
        return queryset


class DashboardView(APIView):
    permission_classes = [FinancePermission]

    def get(self, request):
        user = request.user
        queryset = Budget.objects.filter(organization=user.organization)
        
        budget_total = queryset.aggregate(total=Sum('montant'))['total'] or 0
        dons_total = Don.objects.filter(organization=user.organization).aggregate(total=Sum('montant'))['total'] or 0
        depenses_total = Depense.objects.filter(organization=user.organization).aggregate(total=Sum('montant'))['total'] or 0
        solde = dons_total - depenses_total
        
        taux_execution = 0
        if budget_total > 0:
            taux_execution = round((depenses_total / budget_total) * 100, 2)
        
        return Response({
            "budget_total": float(budget_total),
            "dons_reçus": float(dons_total),
            "depenses_totales": float(depenses_total),
            "solde_disponible": float(solde),
            "taux_execution": taux_execution,
        })


class BudgetListCreateView(FinanceQuerysetMixin, generics.ListCreateAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [FinancePermission]
    queryset = Budget.objects.select_related("projet")

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization, created_by=self.request.user)


class BudgetDetailView(FinanceQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [FinancePermission]
    queryset = Budget.objects.all()
    lookup_url_kwarg = "id"


class DonListCreateView(FinanceQuerysetMixin, generics.ListCreateAPIView):
    serializer_class = DonSerializer
    permission_classes = [FinancePermission]
    queryset = Don.objects.select_related("projet", "campagne", "budget")

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization, created_by=self.request.user)


class DonDetailView(FinanceQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DonSerializer
    permission_classes = [FinancePermission]
    queryset = Don.objects.all()
    lookup_url_kwarg = "id"


class DepenseListCreateView(FinanceQuerysetMixin, generics.ListCreateAPIView):
    serializer_class = DepenseSerializer
    permission_classes = [FinancePermission]
    queryset = Depense.objects.select_related("projet", "campagne")

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization, created_by=self.request.user)


class DepenseDetailView(FinanceQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DepenseSerializer
    permission_classes = [FinancePermission]
    queryset = Depense.objects.all()
    lookup_url_kwarg = "id"


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
    queryset = Justification.objects.all()
    lookup_url_kwarg = "id"

    def get_queryset(self):
        queryset = Justification.objects.filter(depense__organization=self.request.user.organization)
        return queryset


class BudgetAnalysisView(APIView):
    permission_classes = [FinancePermission]

    def get(self, request, campaign_id):
        # Préparer les données pour l'analyse IA
        data = prepare_budget_analysis(campaign_id)
        
        # Envoyer à FastAPI pour l'analyse
        try:
            import requests
            fastapi_url = f"http://ia_service:8001/api/ia/budget-analysis/{campaign_id}"
            response = requests.post(fastapi_url, json=data, timeout=10)
            if response.status_code == 200:
                ia_analysis = response.json()
                return Response({
                    "financial_data": data,
                    "ia_analysis": ia_analysis
                })
            else:
                return Response({
                    "financial_data": data,
                    "ia_analysis": None,
                    "error": "IA service unavailable"
                })
        except Exception as e:
            return Response({
                "financial_data": data,
                "ia_analysis": None,
                "error": str(e)
            })