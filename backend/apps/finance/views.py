from django.db.models import Sum, Q, F
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import FileResponse, Http404
from pathlib import Path
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
import requests
import logging

logger = logging.getLogger(__name__)

from .models import Budget, Don, Depense, Justification, Bailleur, Partenaire, LigneBudgetaire, Donateur, Financement
from .serializers import (
    BudgetSerializer,
    DonSerializer,
    DepenseSerializer,
    JustificationSerializer,
    BailleurSerializer,
    PartenaireSerializer,
    LigneBudgetaireSerializer,
    DonateurSerializer,
    FinancementSerializer,
)
from .permissions import FinancePermission
from .services import (
    calculate_financial_kpis,
    build_finance_dashboard,
    prepare_budget_analysis,
    save_financially_locked,
    delete_financially_locked,
)
from apps.campaigns.models import Campaign
from apps.common.scoping import scope_by_organization, user_organization
from apps.common.interservice import post_to_ai_service, ai_tenant_identity
from apps.ia.guardrails import input_guardrail_message, out_of_scope_message, safe_audit_text
from rest_framework.exceptions import NotFound
from apps.accounts.permissions import IsAccountActive, IsGerant


# -------------------------------------------------------------------
# Pagination personnalisée
# -------------------------------------------------------------------
class FinancePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class FinanceSearchListMixin:
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        search = (self.request.query_params.get("search") or "").strip()
        if search:
            queryset = queryset.filter(nom__icontains=search)
        return queryset.order_by("nom", "pk")

    def paginate_queryset(self, queryset):
        if not (self.request.query_params.get("search") or self.request.query_params.get("page")):
            return None
        if not hasattr(self, "_search_paginator"):
            self._search_paginator = FinancePagination()
        return self._search_paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        return self._search_paginator.get_paginated_response(data)


# -------------------------------------------------------------------
# Filtre Organisation
# -------------------------------------------------------------------
class FinanceQuerysetMixin:
    def get_queryset(self):
        queryset = scope_by_organization(self.queryset, self.request.user)
        user = self.request.user
        if user.role == "SUPER_ADMIN" or not user.organization_id:
            return queryset

        org_id = user.organization_id
        model_name = queryset.model.__name__
        if model_name == "Budget":
            return queryset.filter(projet__organization_id=org_id)
        if model_name == "LigneBudgetaire":
            return queryset.filter(
                budget__organization_id=org_id,
                budget__projet__organization_id=org_id,
            )
        if model_name == "Depense":
            return (
                queryset
                .filter(Q(projet__isnull=True) | Q(projet__organization_id=org_id))
                .filter(Q(budget__isnull=True) | Q(
                    budget__organization_id=org_id,
                    budget__projet__organization_id=org_id,
                ))
                .filter(Q(ligne_budgetaire__isnull=True) | Q(
                    ligne_budgetaire__organization_id=org_id,
                    ligne_budgetaire__budget__organization_id=org_id,
                    ligne_budgetaire__budget__projet__organization_id=org_id,
                ))
                .filter(Q(campagne__isnull=True) | Q(
                    campagne__organization_id=org_id,
                    campagne__projet__organization_id=org_id,
                ))
                .filter(Q(budget__isnull=True) | Q(projet__isnull=True) | Q(budget__projet_id=F("projet_id")))
                .filter(Q(ligne_budgetaire__isnull=True) | Q(budget__isnull=True) | Q(ligne_budgetaire__budget_id=F("budget_id")))
                .filter(Q(campagne__isnull=True) | Q(projet__isnull=True) | Q(campagne__projet_id=F("projet_id")))
            )
        if model_name == "Financement":
            return (
                queryset.filter(projet__organization_id=org_id)
                .filter(Q(budget__isnull=True) | Q(
                    budget__organization_id=org_id,
                    budget__projet__organization_id=org_id,
                    budget__projet_id=F("projet_id"),
                ))
                .filter(Q(campagne__isnull=True) | Q(
                    campagne__organization_id=org_id,
                    campagne__projet__organization_id=org_id,
                    campagne__projet_id=F("projet_id"),
                ))
                .filter(Q(bailleur__isnull=True) | Q(bailleur__organization_id=org_id))
            )
        if model_name == "Don":
            return (
                queryset
                .filter(Q(donateur__isnull=True) | Q(donateur__organization_id=org_id))
                .filter(Q(campagne__isnull=True) | Q(
                    campagne__organization_id=org_id,
                    campagne__projet__organization_id=org_id,
                ))
            )
        return queryset


# -------------------------------------------------------------------
# Dashboard
# -------------------------------------------------------------------
class FinanceDashboardView(APIView):
    permission_classes = [FinancePermission]

    def get(self, request):
        return Response(build_finance_dashboard(request.user.organization))


# -------------------------------------------------------------------
# Lignes Budgétaires
# -------------------------------------------------------------------
class LigneBudgetaireListCreateView(FinanceQuerysetMixin, generics.ListCreateAPIView):
    queryset = LigneBudgetaire.objects.select_related("budget")
    serializer_class = LigneBudgetaireSerializer
    permission_classes = [FinancePermission]

    def perform_create(self, serializer):
        save_financially_locked(serializer, self.request.user)


class LigneBudgetaireDetailView(FinanceQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = LigneBudgetaire.objects.all()
    serializer_class = LigneBudgetaireSerializer
    permission_classes = [FinancePermission]
    lookup_field = "id"

    def perform_update(self, serializer):
        save_financially_locked(serializer, self.request.user)

    def perform_destroy(self, instance):
        delete_financially_locked(instance, self.request.user)


# -------------------------------------------------------------------
# Donateurs
# -------------------------------------------------------------------
class DonateurListCreateView(FinanceSearchListMixin, FinanceQuerysetMixin, generics.ListCreateAPIView):
    queryset = Donateur.objects.all()
    serializer_class = DonateurSerializer
    permission_classes = [FinancePermission]

    def perform_create(self, serializer):
        organization = user_organization(self.request.user)
        if organization is None:
            self.permission_denied(self.request, message="Aucune organisation associée.")
        serializer.save(organization=organization)


class DonateurDetailView(FinanceQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Donateur.objects.all()
    serializer_class = DonateurSerializer
    permission_classes = [FinancePermission]
    lookup_field = "id"


# -------------------------------------------------------------------
# Financements
# -------------------------------------------------------------------
class FinancementListCreateView(FinanceQuerysetMixin, generics.ListCreateAPIView):
    queryset = Financement.objects.select_related("projet", "budget", "bailleur", "campagne")
    serializer_class = FinancementSerializer
    permission_classes = [FinancePermission]

    def perform_create(self, serializer):
        save_financially_locked(serializer, self.request.user)


class FinancementDetailView(FinanceQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Financement.objects.all()
    serializer_class = FinancementSerializer
    permission_classes = [FinancePermission]
    lookup_field = "id"

    def perform_update(self, serializer):
        save_financially_locked(serializer, self.request.user)

    def perform_destroy(self, instance):
        delete_financially_locked(instance, self.request.user)


# -------------------------------------------------------------------
# Budgets
# -------------------------------------------------------------------
class BudgetListCreateView(FinanceQuerysetMixin, generics.ListCreateAPIView):
    queryset = Budget.objects.select_related("projet")
    serializer_class = BudgetSerializer
    permission_classes = [FinancePermission]

    def perform_create(self, serializer):
        org = user_organization(self.request.user)
        if org is None:
            self.permission_denied(self.request, message="Aucune organisation associée.")
        save_financially_locked(serializer, self.request.user)


class BudgetDetailView(FinanceQuerysetMixin,
                       generics.RetrieveUpdateDestroyAPIView):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [FinancePermission]
    lookup_field = "id"

    def perform_update(self, serializer):
        save_financially_locked(serializer, self.request.user)

    def perform_destroy(self, instance):
        delete_financially_locked(instance, self.request.user)


# -------------------------------------------------------------------
# Dons
# -------------------------------------------------------------------
class DonListCreateView(FinanceQuerysetMixin, generics.ListCreateAPIView):
    queryset = Don.objects.select_related("donateur", "campagne")
    serializer_class = DonSerializer
    permission_classes = [FinancePermission]

    def perform_create(self, serializer):
        save_financially_locked(serializer, self.request.user)


class DonDetailView(FinanceQuerysetMixin,
                    generics.RetrieveUpdateDestroyAPIView):
    queryset = Don.objects.all()
    serializer_class = DonSerializer
    permission_classes = [FinancePermission]
    lookup_field = "id"

    def perform_update(self, serializer):
        save_financially_locked(serializer, self.request.user)

    def perform_destroy(self, instance):
        delete_financially_locked(instance, self.request.user)


# -------------------------------------------------------------------
# Dépenses
# -------------------------------------------------------------------
class DepenseListCreateView(FinanceQuerysetMixin,
                            generics.ListCreateAPIView):
    queryset = Depense.objects.select_related("budget__projet", "campagne").prefetch_related("justifications")
    serializer_class = DepenseSerializer
    permission_classes = [FinancePermission]

    def perform_create(self, serializer):
        save_financially_locked(serializer, self.request.user)


class DepenseDetailView(FinanceQuerysetMixin,
                        generics.RetrieveUpdateDestroyAPIView):
    queryset = Depense.objects.all()
    serializer_class = DepenseSerializer
    permission_classes = [FinancePermission, IsAccountActive]
    lookup_field = "id"

    def perform_update(self, serializer):
        save_financially_locked(serializer, self.request.user)

    def perform_destroy(self, instance):
        delete_financially_locked(instance, self.request.user)


# -------------------------------------------------------------------
# Justifications
# -------------------------------------------------------------------
class JustificationListCreateView(generics.ListCreateAPIView):
    serializer_class = JustificationSerializer
    permission_classes = [FinancePermission, IsAccountActive]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return scope_by_organization(
            Justification.objects.filter(depense_id=self.kwargs["depense_id"]),
            self.request.user,
            lookup="depense__organization",
        )

    def perform_create(self, serializer):
        depense = scope_by_organization(
            Depense.objects.filter(id=self.kwargs["depense_id"]),
            self.request.user,
        ).first()
        if not depense:
            raise NotFound("Dépense introuvable.")
        justification = serializer.save(
            depense=depense,
            uploaded_by=self.request.user,
        )
        # Mettre à jour le statut de la dépense
        depense = justification.depense
        if depense.statut == Depense.Status.EN_ATTENTE:
            depense.statut = Depense.Status.VERIFIE
            depense.save(update_fields=['statut'])


class JustificationDetailView(generics.DestroyAPIView):
    serializer_class = JustificationSerializer
    permission_classes = [FinancePermission]
    lookup_field = "id"

    def get_queryset(self):
        return scope_by_organization(
            Justification.objects.all(),
            self.request.user,
            lookup="depense__organization",
        )


class JustificationDocumentView(APIView):
    permission_classes = [FinancePermission, IsAccountActive]

    def get(self, request, id):
        justification = scope_by_organization(
            Justification.objects.select_related("depense").all(),
            request.user,
            lookup="depense__organization",
        ).filter(id=id).first()
        if not justification or not justification.fichier:
            raise Http404
        response = FileResponse(
            justification.fichier.open("rb"), as_attachment=True,
            filename=Path(justification.fichier.name).name,
        )
        response["X-Content-Type-Options"] = "nosniff"
        response["Cache-Control"] = "private, no-store"
        return response


# -------------------------------------------------------------------
# Assistant IA
# -------------------------------------------------------------------
class BudgetAnalysisView(APIView):
    permission_classes = [FinancePermission]

    FASTAPI_URL = "http://ia_service:8001/api/ia/budget-analysis"

    def get(self, request, campaign_id):
        user = request.user
        if user.role not in {"GERANT", "FINANCE", "SUPER_ADMIN"}:
            return Response({"detail": "Accès réservé aux responsables financiers."}, status=status.HTTP_403_FORBIDDEN)
        campaign_qs = Campaign.objects.filter(
            id=campaign_id,
            projet__organization_id=F("organization_id"),
        )
        if user.role != "SUPER_ADMIN":
            if not user.organization_id:
                campaign_qs = campaign_qs.none()
            else:
                campaign_qs = campaign_qs.filter(organization_id=user.organization_id)
                if user.role == "FINANCE":
                    campaign_qs = campaign_qs.filter(projet__responsable_finance=user)
        campaign = campaign_qs.first()
        if not campaign:
            return Response({"detail": "Campagne introuvable."}, status=status.HTTP_404_NOT_FOUND)

        financial_data = prepare_budget_analysis(campaign.id)

        try:
            response = post_to_ai_service(
                self.FASTAPI_URL,
                payload=financial_data,
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


# -------------------------------------------------------------------
# Bailleurs
# -------------------------------------------------------------------
class BailleurListCreateView(FinanceSearchListMixin, FinanceQuerysetMixin, generics.ListCreateAPIView):
    queryset = Bailleur.objects.all()
    serializer_class = BailleurSerializer
    permission_classes = [FinancePermission]

    def perform_create(self, serializer):
        org = user_organization(self.request.user)
        if org is None:
            self.permission_denied(self.request, message="Aucune organisation associée.")
        serializer.save(organization=org)


class BailleurDetailView(FinanceQuerysetMixin,
                         generics.RetrieveUpdateDestroyAPIView):
    queryset = Bailleur.objects.all()
    serializer_class = BailleurSerializer
    permission_classes = [FinancePermission]
    lookup_field = "id"


# -------------------------------------------------------------------
# Partenaires
# -------------------------------------------------------------------
class PartenaireListCreateView(FinanceSearchListMixin, FinanceQuerysetMixin, generics.ListCreateAPIView):
    queryset = Partenaire.objects.all()
    serializer_class = PartenaireSerializer
    permission_classes = [FinancePermission]

    def perform_create(self, serializer):
        org = user_organization(self.request.user)
        if org is None:
            self.permission_denied(self.request, message="Aucune organisation associée.")
        serializer.save(organization=org)


class PartenaireDetailView(FinanceQuerysetMixin,
                           generics.RetrieveUpdateDestroyAPIView):
    queryset = Partenaire.objects.all()
    serializer_class = PartenaireSerializer
    permission_classes = [FinancePermission]
    lookup_field = "id"


# -------------------------------------------------------------------
# Assistant IA Finance — Chat conversationnel
# -------------------------------------------------------------------
import json
import decimal
import datetime as dt
import uuid as uuid_mod
import logging

logger = logging.getLogger(__name__)


def build_finance_chat_context(user):
    """
    Collecte toutes les données financières réelles depuis PostgreSQL.
    Aucune donnée fictive — tout provient de la base de données.
    """
    from django.utils import timezone
    from django.db.models import Sum, Count, CharField
    from django.db.models.functions import Coalesce
    from apps.campaigns.models import Campaign

    org  = user.organization
    financial_kpis = calculate_financial_kpis(org)
    now  = timezone.now()
    today = now.date()

    # ── Budgets ──────────────────────────────────────────────────────
    budgets_qs = Budget.objects.filter(
        organization=org, projet__organization=org,
    ).select_related("projet")
    budget_total = financial_kpis["budget_total"]

    budgets_data = [
        {
            "id":               str(b.id),
            "projet":           b.projet.name if b.projet else "—",
            "montant":          float(b.montant),
            "statut":           b.statut,
            "source":           b.source_financement,
            "date":             b.date.isoformat() if b.date else None,
            "financements_recus": float(b.total_financements_recus),
            "total_depenses":   float(b.total_depenses),
            "solde_budgetaire": float(b.solde),
            "taux_execution":   float(b.taux_execution),
        }
        for b in budgets_qs[:15]
    ]

    # ── Dons ─────────────────────────────────────────────────────────
    dons_qs     = Don.objects.filter(organization=org).filter(
        Q(donateur__isnull=True) | Q(donateur__organization=org),
        Q(campagne__isnull=True) | Q(campagne__organization=org, campagne__projet__organization=org),
    )
    dons_total  = financial_kpis["dons_recus"]

    dons_data = [
        {
            "reference":        d.reference,
            "donateur":         d.donateur.nom if d.donateur else None,
            "montant":          float(d.montant),
            "moyen_paiement":   d.moyen_paiement,
            "date":             d.date.isoformat() if d.date else None,
            "campagne":         d.campagne.nom if d.campagne else None,
        }
        for d in dons_qs.order_by("-date")[:10]
    ]

    # ── Dépenses ─────────────────────────────────────────────────────
    depenses_qs    = Depense.objects.filter(
        organization=org,
        statut=Depense.Status.APPROUVE,
    ).filter(
        Q(projet__isnull=True) | Q(projet__organization=org),
        Q(budget__isnull=True) | Q(budget__organization=org, budget__projet__organization=org),
        Q(ligne_budgetaire__isnull=True) | Q(
            ligne_budgetaire__organization=org,
            ligne_budgetaire__budget__organization=org,
            ligne_budgetaire__budget__projet__organization=org,
        ),
        Q(campagne__isnull=True) | Q(campagne__organization=org, campagne__projet__organization=org),
    )
    depenses_total = financial_kpis["depenses_validees"]

    dep_par_categorie = {
        k: float(v)
        for k, v in depenses_qs.values("categorie")
        .annotate(total=Sum("montant"))
        .values_list("categorie", "total")
        if k and v is not None
    }

    dep_par_region = {
        region_name: float(total)
        for region_name, total in depenses_qs.annotate(
            region_name=Coalesce(
                "projet__region",
                "budget__projet__region",
                "campagne__projet__region",
                output_field=CharField(),
            )
        ).values("region_name").annotate(total=Sum("montant")).values_list("region_name", "total")
        if region_name and total is not None
    }

    dep_par_statut = dict(
        depenses_qs.values("statut")
        .annotate(nb=Count("id"))
        .values_list("statut", "nb")
    )

    # Dépenses des 14 derniers jours vs 14 précédents (détection accélération)
    from datetime import timedelta
    cutoff_14  = today - timedelta(days=14)
    cutoff_28  = today - timedelta(days=28)
    dep_14j    = float(depenses_qs.filter(date__gte=cutoff_14)
                       .aggregate(t=Sum("montant"))["t"] or 0)
    dep_14_28j = float(depenses_qs.filter(date__gte=cutoff_28, date__lt=cutoff_14)
                       .aggregate(t=Sum("montant"))["t"] or 0)

    # ── Justificatifs ─────────────────────────────────────────────────
    just_qs = Justification.objects.filter(depense__organization=org)
    total_just     = just_qs.count()
    conformes      = just_qs.filter(statut="CONFORME").count()
    a_verifier     = just_qs.filter(statut="A_VERIFIER").count()
    non_conformes  = just_qs.filter(statut="NON_CONFORME").count()

    taux_conformite = round((conformes / total_just * 100), 1) if total_just > 0 else 0

    # Dépenses sans aucun justificatif
    depenses_sans_just = int(
        depenses_qs.annotate(nb_just=Count("justifications"))
        .filter(nb_just=0).count()
    )

    # ── Campagnes ─────────────────────────────────────────────────────
    campaigns_actives = Campaign.objects.filter(
        organization=org, statut=Campaign.Statut.EN_COURS
    )
    campaigns_data = [
        {
            "id":             str(c.id),
            "nom":            c.nom,
            "date_debut":     c.date_debut.isoformat() if c.date_debut else None,
            "date_fin":       c.date_fin.isoformat() if c.date_fin else None,
            "jours_restants": (c.date_fin - today).days if c.date_fin else None,
        }
        for c in campaigns_actives[:10]
    ]

    # ── Calculs globaux ───────────────────────────────────────────────
    solde = financial_kpis["solde"]

    return {
        "organisation":     str(org) if org else "ONG",
        "date_analyse":     today.isoformat(),
        "finances": {
            "budget_total":              float(budget_total),
            "financements_recus":        financial_kpis["financements_recus"],
            "dons_recus":                float(dons_total),
            "depenses_totales":          float(depenses_total),
            "solde":                     solde,
            "taux_financement":          financial_kpis["taux_financement"],
            "taux_execution":            financial_kpis["taux_execution"],
            "depenses_par_categorie":    dep_par_categorie,
            "depenses_par_region":       dep_par_region,
            "depenses_par_statut":       dep_par_statut,
            "depenses_14_derniers_jours": dep_14j,
            "depenses_14_28_jours":       dep_14_28j,
        },
        "budgets": {
            "total":  int(budgets_qs.count()),
            "liste":  budgets_data,
        },
        "dons": {
            "total":  int(dons_qs.count()),
            "recents": dons_data,
        },
        "justificatifs": {
            "total":              total_just,
            "conformes":          conformes,
            "a_verifier":         a_verifier,
            "non_conformes":      non_conformes,
            "taux_conformite":    taux_conformite,
            "depenses_sans_just": depenses_sans_just,
        },
        "campagnes": {
            "total_actives":  int(campaigns_actives.count()),
            "liste":          campaigns_data,
        },
    }


class FinanceAssistantHomeView(APIView):
    """
    GET /api/finance/assistant/home/
    Détection automatique des risques financiers et état de l'Orb IA pour le Responsable Finance.
    """
    permission_classes = [FinancePermission]

    def get(self, request):
        if request.user.role not in {"GERANT", "FINANCE", "SUPER_ADMIN"}:
            return Response({"detail": "Accès réservé aux responsables financiers."}, status=status.HTTP_403_FORBIDDEN)
        try:
            context = build_finance_chat_context(request.user)
        except Exception as e:
            logger.exception("build_finance_chat_context failed in HomeView (error_type=%s)", type(e).__name__)
            return Response({"detail": "Erreur lors du calcul des indicateurs financiers."}, status=500)

        finances = context.get("finances", {})
        justificatifs = context.get("justificatifs", {})

        budget_total = float(finances.get("budget_total", 0.0))
        depenses = float(finances.get("depenses_totales", 0.0))
        solde = float(finances.get("solde", 0.0))
        taux_execution = float(finances.get("taux_execution", 0.0))

        depenses_sans_just = justificatifs.get("depenses_sans_just", 0)
        a_verifier = justificatifs.get("a_verifier", 0)
        non_conformes = justificatifs.get("non_conformes", 0)

        risques = []
        alert = "GREEN"

        if taux_execution >= 90:
            alert = "RED"
            risques.append("Taux d'exécution critique (> 90%)")
        elif taux_execution >= 75:
            alert = "ORANGE"
            risques.append("Taux d'exécution élevé")
        elif taux_execution >= 50:
            alert = "YELLOW"

        if depenses_sans_just > 0:
            risques.append(f"{depenses_sans_just} justificatif(s) manquant(s)")
            if alert != "RED":
                alert = "ORANGE"

        if non_conformes > 0:
            risques.append(f"{non_conformes} justificatif(s) non conforme(s)")
            alert = "RED"

        if a_verifier > 0:
            risques.append(f"{a_verifier} justificatif(s) à vérifier")
            if alert == "GREEN":
                alert = "YELLOW"

        if solde < 0:
            risques.append("Incohérences financières (solde négatif)")
            alert = "RED"

        if not risques:
            risques.append("Aucun risque financier majeur détecté")

        if alert == "RED":
            observation = f"Situation financière sous tension. Taux d'exécution à {taux_execution:.1f}% avec {len(risques)} risque(s) identifié(s)."
            recommandation = "Auditer d'urgence les dépenses et régulariser les pièces justificatives non conformes."
        elif alert == "ORANGE":
            observation = f"Les dépenses atteignent {depenses:,.0f} FCFA pour un taux d'exécution de {taux_execution:.1f}%. Des risques sont détectés."
            recommandation = "Limiter les dépenses non prioritaires et régulariser les justificatifs manquants."
        elif alert == "YELLOW":
            observation = f"Rythme de dépense modéré ({taux_execution:.1f}% exécutés). Suivi régulier recommandé."
            recommandation = "Planifier les futurs décaissements et valider les pièces en attente."
        else:
            observation = f"Gestion financière saine. Budget total de {budget_total:,.0f} FCFA avec un solde disponible de {solde:,.0f} FCFA."
            recommandation = "Poursuivre le contrôle périodique des dépenses et justificatifs."

        return Response({
            "alert": alert,
            "budget_total": budget_total,
            "depenses": depenses,
            "solde": solde,
            "taux_execution": round(taux_execution, 1),
            "observation": observation,
            "risques": risques,
            "recommandation": recommandation,
        })


class FinanceReportGenerationView(APIView):
    """Generate an organization report from server-built, tenant-scoped data."""

    permission_classes = [FinancePermission]

    def post(self, request):
        if request.user.role not in {"GERANT", "FINANCE", "SUPER_ADMIN"}:
            return Response({"detail": "Accès réservé aux responsables financiers."}, status=status.HTTP_403_FORBIDDEN)
        if request.user.role != "SUPER_ADMIN" and not request.user.organization_id:
            return Response({"detail": "Aucune organisation associée."}, status=status.HTTP_403_FORBIDDEN)
        try:
            context = build_finance_chat_context(request.user)
            response = post_to_ai_service(
                f"{settings.IA_SERVICE_URL.rstrip('/')}/api/ia/rapport/generate",
                payload=context,
                timeout=60,
            )
            response.raise_for_status()
            return Response(response.json())
        except ImproperlyConfigured:
            return Response({"detail": "Le service IA n'est pas configuré."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except requests.RequestException:
            logger.exception("Finance report IA request failed")
            return Response({"detail": "Le service IA est temporairement indisponible."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class FinanceAssistantChatView(APIView):
    """
    POST /api/finance/assistant/chat/
    Assistant IA conversationnel pour le Responsable Finance.
    Utilise les vraies données PostgreSQL — aucune donnée fictive.
    """
    permission_classes = [FinancePermission]

    IA_CHAT_URL = "http://ia_service:8001/api/ia/finance-chat"

    def post(self, request):
        if request.user.role not in {"GERANT", "FINANCE", "SUPER_ADMIN"}:
            return Response({"detail": "Accès réservé aux responsables financiers."}, status=status.HTTP_403_FORBIDDEN)
        question = (request.data.get("question") or "").strip()
        if not question:
            return Response({"detail": "La question ne peut pas être vide."}, status=400)
        blocked_message = input_guardrail_message(question)
        if blocked_message:
            return Response({"answer": blocked_message, "alert": "GREEN", "generated_at": str(dt.datetime.utcnow().isoformat()) + "Z"})
        out_of_scope = out_of_scope_message(question)
        if out_of_scope:
            return Response({"answer": out_of_scope, "alert": "GREEN", "generated_at": str(dt.datetime.utcnow().isoformat()) + "Z"})

        try:
            context = build_finance_chat_context(request.user)
        except Exception as e:
            logger.error("build_finance_chat_context failed (error_type=%s)", type(e).__name__)
            return Response({"detail": "Erreur lors de la collecte des données financières."}, status=500)

        class _SafeEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, decimal.Decimal):
                    return float(obj)
                if isinstance(obj, (dt.date, dt.datetime)):
                    return obj.isoformat()
                if isinstance(obj, uuid_mod.UUID):
                    return str(obj)
                return super().default(obj)

        payload_bytes = json.dumps(
            {
                "question": question,
                "context": context,
                "tenant": ai_tenant_identity(request.user),
            },
            cls=_SafeEncoder,
        ).encode("utf-8")

        alert_level = "GREEN"
        finances = context.get("finances", {})
        bt = finances.get("budget_total", 0)
        solde = finances.get("solde", 0)
        taux = finances.get("taux_execution", 0)

        if taux >= 90:
            alert_level = "RED"
        elif taux >= 75:
            alert_level = "ORANGE"
        elif taux >= 60:
            alert_level = "YELLOW"
        else:
            alert_level = "GREEN"

        raw_answer = None

        try:
            resp = post_to_ai_service(
                self.IA_CHAT_URL,
                body=payload_bytes,
                headers={"Content-Type": "application/json"},
                timeout=120,
            )
            resp.raise_for_status()
            res_json = resp.json()
            raw_answer = res_json.get("answer")
            alert_level = res_json.get("alert", alert_level)
        except Exception as e:
            logger.error("FinanceAssistantChatView IA call failed (error_type=%s)", type(e).__name__)
            raw_answer = None

        # Construire une réponse string propre depuis raw_answer ou les données du contexte
        def build_answer_string(raw, bt, solde, taux, alert_lvl):
            if isinstance(raw, str) and raw.strip():
                return raw.strip()

            if isinstance(raw, dict) and raw.get("answer"):
                inner = raw["answer"]
                if isinstance(inner, str):
                    return inner.strip()

            # Fallback basé sur les données financières réelles
            bt_fmt   = f"{bt:,.0f}".replace(",", " ")
            solde_fmt = f"{solde:,.0f}".replace(",", " ")
            lines = [
                f"**Synthèse financière**\n",
                f"- Budget total : **{bt_fmt} FCFA**",
                f"- Taux d'exécution : **{taux:.1f}%**",
                f"- Solde disponible : **{solde_fmt} FCFA**\n",
            ]
            if alert_lvl == "RED":
                lines.append("⚠️ La situation est critique. Le budget est presque épuisé.")
                lines.append("\n**Recommandation :** Suspendez les dépenses non prioritaires immédiatement et auditez les postes les plus consommateurs.")
            elif alert_lvl == "ORANGE":
                lines.append("⚠️ Le rythme des dépenses est élevé. Une attention particulière est nécessaire.")
                lines.append("\n**Recommandation :** Limitez les nouvelles dépenses et vérifiez les justificatifs en attente.")
            elif alert_lvl == "YELLOW":
                lines.append("Le rythme de dépense est modéré. Un suivi régulier est recommandé.")
                lines.append("\n**Recommandation :** Planifiez les futurs décaissements et validez les pièces en attente.")
            else:
                lines.append("La gestion financière est saine.")
                lines.append("\n**Recommandation :** Poursuivez le contrôle périodique des dépenses.")

            return "\n".join(lines)

        final_answer = build_answer_string(raw_answer, bt, solde, taux, alert_level)
        final_answer = safe_audit_text(final_answer, limit=4000)

        return Response({
            "alert": alert_level,
            "answer": final_answer,
            "generated_at": str(dt.datetime.utcnow().isoformat()) + "Z",
        })
# -------------------------------------------------------------------
# Budgets - Approuver (Gérant)
# -------------------------------------------------------------------
from rest_framework.response import Response
from rest_framework import status as http_status


class BudgetApprovalView(APIView):
    """
    Vue pour permettre au Gérant d'approuver les budgets en attente.
    """
    permission_classes = [IsGerant]

    def get(self, request):
        # Le gérant voit les budgets de son organisation
        org = request.user.organization
        budgets = Budget.objects.filter(
            organization=org, projet__organization=org,
            statut__in=[Budget.Status.BROUILLON, Budget.Status.EN_COURS]
        ).select_related("projet").order_by("-created_at")

        from .serializers import BudgetSerializer
        serializer = BudgetSerializer(budgets, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Approuver ou rejeter un budget"""
        budget_id = request.data.get("budget_id")
        action_type = request.data.get("action", "").upper()

        if not budget_id:
            return Response(
                {"error": "budget_id est requis"},
                status=http_status.HTTP_400_BAD_REQUEST
            )

        # Accepter aussi bien "approve" que "APPROUVER"
        if action_type in ["APPROVE", "APPROUVER"]:
            action_type = "APPROUVER"
        elif action_type in ["REJECT", "REJETER"]:
            action_type = "REJETER"

        try:
            budget = Budget.objects.get(
                id=budget_id, organization=request.user.organization,
                projet__organization=request.user.organization,
            )
        except Budget.DoesNotExist:
            return Response(
                {"error": "Budget non trouvé"},
                status=http_status.HTTP_404_NOT_FOUND
            )

        if action_type == "APPROUVER":
            budget.statut = Budget.Status.APPROUVE
            budget.save()
            return Response({"message": "Budget approuvé", "statut": budget.statut})
        elif action_type == "REJETER":
            budget.statut = Budget.Status.BROUILLON
            budget.save()
            return Response({"message": "Budget rejeté", "statut": budget.statut})
        else:
            return Response(
                {"error": f"Action invalide: {action_type}"},
                status=http_status.HTTP_400_BAD_REQUEST
            )
