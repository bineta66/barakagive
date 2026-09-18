from django.db import transaction
from django.db.models import Sum
from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Bailleur, Budget, Depense, Don, Justificatif, Partenaire, PosteBudgetaire
from .permissions import (
    FinancePermission,
    JustificatifPermission,
    OrganizationManagerPermission,
    SuperAdminPermission,
)
from .serializers import (
    BailleurSerializer, BudgetSerializer, DepenseSerializer, DonSerializer,
    JustificatifSerializer, PartenaireSerializer, PosteBudgetaireSerializer,
)
from .services import recalculate_poste


class OrganizationQuerysetMixin:
    scope_to_project = False

    def org_queryset(self, queryset):
        if self.request.user.role != "SUPER_ADMIN":
            queryset = queryset.filter(organization=self.request.user.organization)
        if self.scope_to_project and self.request.user.role == "CHEF_PROJET":
            queryset = queryset.filter(projet__chef_projet=self.request.user)
        return queryset


class BailleurListCreateView(OrganizationQuerysetMixin, generics.ListCreateAPIView):
    serializer_class = BailleurSerializer
    permission_classes = [OrganizationManagerPermission]

    def get_queryset(self):
        return self.org_queryset(Bailleur.objects.all())

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization, created_by=self.request.user)


class BailleurDetailView(OrganizationQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BailleurSerializer
    permission_classes = [OrganizationManagerPermission]
    lookup_url_kwarg = "id"

    def get_queryset(self):
        return self.org_queryset(Bailleur.objects.all())


class PartenaireListCreateView(OrganizationQuerysetMixin, generics.ListCreateAPIView):
    serializer_class = PartenaireSerializer
    permission_classes = [OrganizationManagerPermission]

    def get_queryset(self):
        return self.org_queryset(Partenaire.objects.all())

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization, created_by=self.request.user)


class PartenaireDetailView(OrganizationQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PartenaireSerializer
    permission_classes = [OrganizationManagerPermission]
    lookup_url_kwarg = "id"

    def get_queryset(self):
        return self.org_queryset(Partenaire.objects.all())


class DonListCreateView(OrganizationQuerysetMixin, generics.ListCreateAPIView):
    serializer_class = DonSerializer
    permission_classes = [FinancePermission]
    scope_to_project = True

    def get_queryset(self):
        return self.org_queryset(Don.objects.select_related("bailleur", "projet"))

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization, created_by=self.request.user)


class DonDetailView(OrganizationQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DonSerializer
    permission_classes = [FinancePermission]
    lookup_url_kwarg = "id"
    scope_to_project = True

    def get_queryset(self):
        return self.org_queryset(Don.objects.all())


class BudgetListCreateView(OrganizationQuerysetMixin, generics.ListCreateAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [FinancePermission]
    scope_to_project = True

    def get_queryset(self):
        return self.org_queryset(Budget.objects.select_related("projet", "don").prefetch_related("postes"))

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization, created_by=self.request.user)


class BudgetDetailView(OrganizationQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [FinancePermission]
    lookup_url_kwarg = "id"
    scope_to_project = True

    def get_queryset(self):
        return self.org_queryset(Budget.objects.prefetch_related("postes"))


class PosteListCreateView(generics.ListCreateAPIView):
    serializer_class = PosteBudgetaireSerializer
    permission_classes = [FinancePermission]

    def get_queryset(self):
        queryset = PosteBudgetaire.objects.filter(
            budget_id=self.kwargs["budget_id"],
            budget__organization=self.request.user.organization,
        )
        if self.request.user.role == "CHEF_PROJET":
            queryset = queryset.filter(budget__projet__chef_projet=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(budget_id=self.kwargs["budget_id"])


class PosteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PosteBudgetaireSerializer
    permission_classes = [FinancePermission]
    lookup_url_kwarg = "id"

    def get_queryset(self):
        queryset = PosteBudgetaire.objects.filter(budget__organization=self.request.user.organization)
        if self.request.user.role == "CHEF_PROJET":
            queryset = queryset.filter(budget__projet__chef_projet=self.request.user)
        return queryset


class DepenseListCreateView(OrganizationQuerysetMixin, generics.ListCreateAPIView):
    serializer_class = DepenseSerializer
    permission_classes = [FinancePermission]
    scope_to_project = True

    def get_queryset(self):
        return self.org_queryset(Depense.objects.select_related("projet", "poste_budgetaire").prefetch_related("justificatifs"))


class DepenseDetailView(OrganizationQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DepenseSerializer
    permission_classes = [FinancePermission]
    lookup_url_kwarg = "id"
    scope_to_project = True

    def get_queryset(self):
        return self.org_queryset(Depense.objects.prefetch_related("justificatifs"))


class JustificatifListCreateView(generics.ListCreateAPIView):
    serializer_class = JustificatifSerializer
    permission_classes = [JustificatifPermission]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Justificatif.objects.filter(
            depense_id=self.kwargs["depense_id"],
            depense__organization=self.request.user.organization,
        )

    def perform_create(self, serializer):
        serializer.save(
            depense_id=self.kwargs["depense_id"],
            uploaded_by=self.request.user,
        )


class JustificatifDetailView(generics.DestroyAPIView):
    serializer_class = JustificatifSerializer
    permission_classes = [SuperAdminPermission]
    lookup_url_kwarg = "id"

    def get_queryset(self):
        queryset = Justificatif.objects.all()
        if self.request.user.role != "SUPER_ADMIN":
            queryset = queryset.filter(depense__organization=self.request.user.organization)
        return queryset


class DepenseStatusView(APIView):
    permission_classes = [SuperAdminPermission]

    @transaction.atomic
    def patch(self, request, id):
        try:
            depense = Depense.objects.get(id=id, organization=request.user.organization)
        except Depense.DoesNotExist:
            return Response({"detail": "Dépense introuvable."}, status=status.HTTP_404_NOT_FOUND)
        new_status = request.data.get("statut")
        if new_status not in {Depense.Status.APPROUVEE, Depense.Status.REJETEE}:
            return Response({"detail": "Statut invalide."}, status=status.HTTP_400_BAD_REQUEST)
        depense.statut = new_status
        depense.save(update_fields=["statut", "updated_at"])
        recalculate_poste(depense.poste_budgetaire)
        return Response(DepenseSerializer(depense, context={"request": request}).data)


class FinanceDashboardView(APIView):
    permission_classes = [FinancePermission]

    def get(self, request):
        budgets = Budget.objects.all()
        depenses = Depense.objects.all()
        dons = Don.objects.all()
        if request.user.role != "SUPER_ADMIN":
            budgets = budgets.filter(organization=request.user.organization)
            depenses = depenses.filter(organization=request.user.organization)
            dons = dons.filter(organization=request.user.organization)
        budget_total = budgets.aggregate(total=Sum("montant_total"))["total"] or 0
        montant_finance = dons.aggregate(total=Sum("montant_affecte"))["total"] or 0
        montant_depense = depenses.filter(statut=Depense.Status.APPROUVEE).aggregate(total=Sum("montant"))["total"] or 0
        return Response({
            "budget_total": budget_total,
            "montant_finance": montant_finance,
            "montant_depense": montant_depense,
            "solde": budget_total - montant_depense,
            "nb_budgets": budgets.count(),
            "nb_depenses": depenses.count(),
        })
