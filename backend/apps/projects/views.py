from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.accounts.permissions import IsAccountActive
from django.conf import settings
import requests
import json
import re
import logging
import unicodedata
from django.db.models import Avg, Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import date, timedelta
from uuid import UUID

from drf_spectacular.utils import extend_schema

from .models import Project, ProjectCriteria
from .serializers import (
    ProjectSerializer,
    ProjectCreateSerializer,
    BudgetUpdateSerializer,
    ProjectCriteriaSerializer,
    ProjectCriteriaCreateSerializer,
)
from .permissions import (
    IsGerantOrFinanceOrAgent,
    CanManageProject,
    CanManageProjectCriteria,
)
from apps.common.scoping import scope_by_organization
from apps.campaigns.models import Campaign
from apps.beneficiaries.models import Beneficiary, FormResponse, HumanitarianAction
from apps.finance.models import Budget, Depense, Don, Financement
from apps.zones.models import Zone

logger = logging.getLogger(__name__)
from apps.common.interservice import post_to_ai_service, ai_tenant_identity
from apps.common.pagination import StandardPagination


@extend_schema(tags=["Projets"])
class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAccountActive, IsGerantOrFinanceOrAgent, CanManageProject]
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = scope_by_organization(
            Project.objects.select_related(
                "chef_projet", "responsable_finance", "organization", "created_by"
            ).prefetch_related("criteres").order_by("name", "pk"),
            self.request.user,
        )
        user = self.request.user
        if user.role == "CHEF_PROJET":
            queryset = queryset.filter(chef_projet=user)
        elif user.role == "FINANCE":
            queryset = queryset.filter(responsable_finance=user)
        elif user.role == "AGENT":
            queryset = queryset.filter(campaigns__affectations__agent=user).distinct()
        archived = self.request.query_params.get("archived")
        if archived is not None:
            queryset = queryset.filter(archived=archived.lower() in {"1", "true", "yes"})
        region = (self.request.query_params.get("region") or "").strip()
        if region:
            queryset = queryset.filter(region__iexact=region)
        search = (self.request.query_params.get("search") or "").strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(code__icontains=search)
                | Q(region__icontains=search)
            )
        raw_ids = (self.request.query_params.get("ids") or "").strip()
        if raw_ids:
            ids = [value for value in raw_ids.split(",")[:100] if value.isdigit()]
            queryset = queryset.filter(pk__in=ids)
        return queryset

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProjectCreateSerializer
        return ProjectSerializer

    def perform_create(self, serializer):
        serializer.save()


@extend_schema(tags=["Tableau de bord"])
class ProjectDecisionDashboardView(APIView):
    """Organization/project KPIs and operational alerts for decision dashboards."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.can_login or user.role not in {"GERANT", "CHEF_PROJET", "FINANCE"} or not user.organization_id:
            return Response({"detail": "Dashboard non autorise."}, status=status.HTTP_403_FORBIDDEN)

        all_projects = Project.objects.filter(organization=user.organization, archived=False)
        if user.role == "CHEF_PROJET":
            all_projects = all_projects.filter(chef_projet=user)
        elif user.role == "FINANCE":
            all_projects = all_projects.filter(responsable_finance=user)
        project_choices = list(all_projects.order_by("name").values("id", "name", "region"))
        project_id = request.query_params.get("project_id")
        try:
            if project_id:
                project_id = int(project_id)
        except (TypeError, ValueError):
            return Response({"detail": "Identifiant de projet invalide."}, status=status.HTTP_400_BAD_REQUEST)
        projects = all_projects.filter(pk=project_id) if project_id else all_projects
        projects = list(projects)
        if project_id and not projects:
            return Response({"detail": "Projet non trouve dans votre perimetre."}, status=status.HTTP_404_NOT_FOUND)
        project_ids = [item.pk for item in projects]

        all_campaigns = Campaign.objects.filter(organization=user.organization, projet_id__in=project_ids).select_related("projet")
        campaign_choices = list(all_campaigns.order_by("nom").values("id", "nom", "projet_id"))
        campaign_id = request.query_params.get("campaign_id")
        try:
            if campaign_id:
                campaign_id = str(UUID(campaign_id))
        except (TypeError, ValueError):
            return Response({"detail": "Identifiant de campagne invalide."}, status=status.HTTP_400_BAD_REQUEST)
        campaigns = all_campaigns.filter(pk=campaign_id) if campaign_id else all_campaigns
        if campaign_id and not campaigns.exists():
            return Response({"detail": "Campagne non trouvee dans votre perimetre."}, status=status.HTTP_404_NOT_FOUND)

        try:
            start_date = date.fromisoformat(request.query_params["start_date"]) if request.query_params.get("start_date") else None
            end_date = date.fromisoformat(request.query_params["end_date"]) if request.query_params.get("end_date") else None
        except ValueError:
            return Response({"detail": "Dates invalides (format attendu AAAA-MM-JJ)."}, status=status.HTTP_400_BAD_REQUEST)
        if start_date and end_date and start_date > end_date:
            return Response({"detail": "La date de debut doit preceder la date de fin."}, status=status.HTTP_400_BAD_REQUEST)
        if start_date or end_date:
            projects = [item for item in projects if (not start_date or item.end_date >= start_date) and (not end_date or item.start_date <= end_date)]
            project_ids = [item.pk for item in projects]
            campaigns = campaigns.filter(projet_id__in=project_ids)
        if start_date:
            campaigns = campaigns.filter(date_fin__gte=start_date)
        if end_date:
            campaigns = campaigns.filter(date_debut__lte=end_date)

        region_id = request.query_params.get("region_id")
        zone_id = request.query_params.get("zone_id")
        try:
            if region_id:
                region_id = int(region_id)
            if zone_id:
                zone_id = str(UUID(zone_id))
        except (TypeError, ValueError):
            return Response({"detail": "Identifiant de region ou de zone invalide."}, status=status.HTTP_400_BAD_REQUEST)
        if region_id:
            campaigns = campaigns.filter(zones__region_id=region_id)
        if zone_id:
            campaigns = campaigns.filter(zones__pk=zone_id)
        campaigns = campaigns.distinct()
        if campaign_id or region_id or zone_id:
            matching_project_ids = set(campaigns.values_list("projet_id", flat=True))
            projects = [item for item in projects if item.pk in matching_project_ids]
            project_ids = [item.pk for item in projects]
        beneficiaries = Beneficiary.objects.filter(campagne__in=campaigns, organization=user.organization).select_related(
            "campagne", "zone", "zone__region"
        )
        if region_id:
            beneficiaries = beneficiaries.filter(zone__region_id=region_id)
        if zone_id:
            beneficiaries = beneficiaries.filter(zone_id=zone_id)
        if start_date:
            beneficiaries = beneficiaries.filter(created_at__date__gte=start_date)
        if end_date:
            beneficiaries = beneficiaries.filter(created_at__date__lte=end_date)

        zones = Zone.objects.filter(organization=user.organization, statut=True, campaigns__in=campaigns)
        region_choices = list(zones.values("region_id", "region__nom").distinct().order_by("region__nom"))
        if region_id:
            zones = zones.filter(region_id=region_id)
        zone_choices = list(zones.values("id", "nom", "region_id", "region__nom").distinct().order_by("nom"))
        today = timezone.localdate()
        late_campaigns = campaigns.filter(date_fin__lt=today, statut__in=[Campaign.Statut.EN_COURS, Campaign.Statut.PLANIFIER])
        campaigns_late = late_campaigns.count()
        priority = beneficiaries.filter(score_vulnerabilite__gte=60)
        priority_count = priority.count()
        waiting_status_count = beneficiaries.filter(
            statut__in=[Beneficiary.Statut.IDENTIFIE, Beneficiary.Statut.EVALUE]
        ).count()
        evaluated_status_count = beneficiaries.filter(statut=Beneficiary.Statut.EVALUE).count()
        priority_status_count = beneficiaries.filter(statut=Beneficiary.Statut.PRIORITAIRE).count()
        taken_care_status_count = beneficiaries.filter(statut=Beneficiary.Statut.PRIS_EN_CHARGE).count()
        exited_status_count = beneficiaries.filter(statut=Beneficiary.Statut.SORTI).count()
        aided_ids = HumanitarianAction.objects.filter(
            beneficiary__in=beneficiaries, statut=HumanitarianAction.Statut.REALISEE
        ).values("beneficiary_id").distinct()
        aided_count = beneficiaries.filter(pk__in=aided_ids).count()
        priority_aided = priority.filter(pk__in=aided_ids).count()
        priority_unassisted = priority_count - priority_aided
        beneficiaries_count = beneficiaries.count()
        beneficiary_levels = {
            "total": beneficiaries_count,
            "evalues": evaluated_status_count,
            "en_attente": waiting_status_count,
            "prioritaires": priority_status_count,
            "pris_en_charge": taken_care_status_count,
            "sortis": exited_status_count,
            "taux_evalues": round(evaluated_status_count / beneficiaries_count * 100, 1) if beneficiaries_count else 0,
            "taux_prioritaires": round(priority_status_count / beneficiaries_count * 100, 1) if beneficiaries_count else 0,
            "taux_pris_en_charge": round(taken_care_status_count / beneficiaries_count * 100, 1) if beneficiaries_count else 0,
        }

        # Financial totals are scoped to the selected projects/campaign and only count received/approved flows.
        budgets = Budget.objects.filter(organization=user.organization, projet_id__in=project_ids)
        financings = Financement.objects.filter(organization=user.organization, projet_id__in=project_ids, statut=Financement.Status.RECU)
        donations = Don.objects.filter(organization=user.organization, campagne__projet_id__in=project_ids)
        expenses = Depense.objects.filter(organization=user.organization, statut=Depense.Status.APPROUVE).filter(
            Q(projet_id__in=project_ids) | Q(budget__projet_id__in=project_ids) | Q(campagne__projet_id__in=project_ids)
        )
        if campaign_id:
            financings = financings.filter(campagne_id=campaign_id)
            donations = donations.filter(campagne_id=campaign_id)
            expenses = expenses.filter(campagne_id=campaign_id)
        # Apply transaction date bounds without changing tenant/project constraints.
        if start_date:
            budgets = budgets.filter(date__gte=start_date)
            financings = financings.filter(date__gte=start_date)
            donations = donations.filter(date__gte=start_date)
            expenses = expenses.filter(date__gte=start_date)
        if end_date:
            budgets = budgets.filter(date__lte=end_date)
            financings = financings.filter(date__lte=end_date)
            donations = donations.filter(date__lte=end_date)
            expenses = expenses.filter(date__lte=end_date)
        budget_total = budgets.aggregate(value=Sum("montant"))["value"] or 0
        financing_total = financings.aggregate(value=Sum("montant"))["value"] or 0
        donation_total = donations.aggregate(value=Sum("montant"))["value"] or 0
        expense_total = expenses.aggregate(value=Sum("montant"))["value"] or 0
        finance = {
            "budget_total": float(budget_total), "financements_recus": float(financing_total),
            "dons_recus": float(donation_total), "depenses_validees": float(expense_total),
            "solde": float(financing_total + donation_total - expense_total),
            "taux_execution": round(float(expense_total / budget_total * 100), 2) if budget_total else 0,
            "taux_financement": round(float((financing_total + donation_total) / budget_total * 100), 2) if budget_total else 0,
        }

        monthly = beneficiaries.annotate(month=TruncMonth("created_at")).values("month").annotate(
            identified=Count("id"),
            evaluated=Count("id", filter=Q(statut__in=[Beneficiary.Statut.EVALUE, Beneficiary.Statut.PRIORITAIRE, Beneficiary.Statut.PRIS_EN_CHARGE])),
            priority=Count("id", filter=Q(score_vulnerabilite__gte=60)),
            aided=Count("id", filter=Q(pk__in=aided_ids)),
        ).order_by("month")
        monthly_series = [{"month": row["month"].strftime("%Y-%m"), "identified": row["identified"],
                           "evaluated": row["evaluated"], "priority": row["priority"], "aided": row["aided"]} for row in monthly if row["month"]]
        finance_months = {}
        for queryset, output_key in ((budgets, "budget"), (financings, "financements"), (donations, "dons"), (expenses, "depenses")):
            rows = queryset.annotate(month=TruncMonth("date")).values("month").annotate(total=Sum("montant"))
            for row in rows:
                if row["month"]:
                    key = row["month"].strftime("%Y-%m")
                    finance_months.setdefault(key, {"month": key, "budget": 0.0, "financements": 0.0, "dons": 0.0, "depenses": 0.0})
                    finance_months[key][output_key] = float(row["total"] or 0)
        finance_series = [finance_months[key] for key in sorted(finance_months)]
        campaign_stats = list(campaigns.values("statut").annotate(total=Count("id")).order_by("statut"))
        late_planned = late_campaigns.filter(statut=Campaign.Statut.PLANIFIER).count()
        late_active = late_campaigns.filter(statut=Campaign.Statut.EN_COURS).count()
        campaigns_chart = [
            {"label": "A preparer", "total": max(0, campaigns.filter(statut__in=[Campaign.Statut.BROUILLON, Campaign.Statut.PLANIFIER]).count() - late_planned)},
            {"label": "En cours", "total": max(0, campaigns.filter(statut=Campaign.Statut.EN_COURS).count() - late_active)},
            {"label": "Terminees", "total": campaigns.filter(statut=Campaign.Statut.TERMINE).count()},
            {"label": "En retard", "total": campaigns_late},
        ]
        zone_stats = list(beneficiaries.values("zone_id", "zone__nom").annotate(
            total=Count("id"), priority=Count("id", filter=Q(score_vulnerabilite__gte=60))
        ).order_by("zone__nom"))
        for row in zone_stats:
            row["aided"] = beneficiaries.filter(zone_id=row["zone_id"], pk__in=aided_ids).count()
            row["zone_id"] = str(row["zone_id"])
            row["nom"] = row.pop("zone__nom")

        project_zone_rows = beneficiaries.values(
            "campagne__projet_id", "zone_id", "zone__nom", "zone__region__nom"
        ).annotate(
            total=Count("id"),
            priority=Count("id", filter=Q(score_vulnerabilite__gte=60)),
            aided=Count("id", filter=Q(pk__in=aided_ids)),
            priority_aided=Count("id", filter=Q(score_vulnerabilite__gte=60, pk__in=aided_ids)),
            average_score=Avg("score_vulnerabilite"),
        ).order_by("campagne__projet_id", "-priority", "-average_score", "zone__nom")
        zones_by_project = {}
        for row in project_zone_rows:
            zones_by_project.setdefault(row["campagne__projet_id"], []).append({
                "id": str(row["zone_id"]),
                "nom": row["zone__nom"],
                "region": row["zone__region__nom"],
                "total": row["total"],
                "prioritaires": row["priority"],
                "pris_en_charge": row["aided"],
                "prioritaires_pris_en_charge": row["priority_aided"],
                "prioritaires_non_couverts": row["priority"] - row["priority_aided"],
                "score_moyen": round(float(row["average_score"]), 1) if row["average_score"] is not None else None,
            })

        project_month_rows = beneficiaries.annotate(month=TruncMonth("created_at")).values(
            "campagne__projet_id", "month"
        ).annotate(total=Count("id")).order_by("campagne__projet_id", "month")
        months_by_project = {}
        for row in project_month_rows:
            if row["month"]:
                months_by_project.setdefault(row["campagne__projet_id"], []).append({
                    "month": row["month"], "total": row["total"]
                })

        late_by_project = dict(late_campaigns.values("projet_id").annotate(total=Count("id")).values_list("projet_id", "total"))
        project_zone_analysis = []
        for project in projects:
            project_zones = zones_by_project.get(project.pk, [])
            total_people = sum(zone["total"] for zone in project_zones)
            total_priority = sum(zone["prioritaires"] for zone in project_zones)
            priority_uncovered = sum(zone["prioritaires_non_couverts"] for zone in project_zones)
            observations = []
            recommendations = []
            if project_zones:
                observations.append(
                    f"{total_people} bénéficiaire(s), dont {total_priority} prioritaire(s), dans {len(project_zones)} zone(s) concernée(s)."
                )
                top_zone = project_zones[0]
                if top_zone["prioritaires"]:
                    observations.append(
                        f"{top_zone['nom']} concentre le plus de bénéficiaires prioritaires ({top_zone['prioritaires']})."
                    )
                if priority_uncovered:
                    target = next((zone for zone in project_zones if zone["prioritaires_non_couverts"]), top_zone)
                    recommendations.append(
                        f"Examiner les {target['prioritaires_non_couverts']} bénéficiaire(s) prioritaire(s) non pris en charge dans {target['nom']}."
                    )
                if total_priority == 0:
                    recommendations.append("Poursuivre l’évaluation des dossiers : aucun score prioritaire n’est enregistré dans le périmètre.")
            else:
                observations.append("Aucun bénéficiaire n’est enregistré dans les zones du périmètre filtré.")
                recommendations.append("Aucune priorité de prise en charge ne peut être établie sans bénéficiaire enregistré.")
            overdue = late_by_project.get(project.pk, 0)
            if overdue:
                observations.append(f"{overdue} campagne(s) du projet sont en retard.")
                recommendations.append("Réexaminer le calendrier des campagnes en retard.")

            forecast = "Prévision indisponible : deux mois consécutifs de données sont nécessaires."
            observed_months = months_by_project.get(project.pk, [])
            if len(observed_months) >= 2:
                previous, latest = observed_months[-2], observed_months[-1]
                month_distance = (latest["month"].year * 12 + latest["month"].month) - (previous["month"].year * 12 + previous["month"].month)
                if month_distance == 1:
                    change = latest["total"] - previous["total"]
                    projected = max(0, latest["total"] + change)
                    next_month = (latest["month"].replace(day=1) + timedelta(days=32)).replace(day=1)
                    forecast = (
                        f"Projection indicative pour {next_month.strftime('%m/%Y')} : environ {projected} bénéficiaire(s) supplémentaire(s), "
                        f"par extrapolation de la variation observée ({change:+d}) entre les deux derniers mois consécutifs."
                    )
            project_zone_analysis.append({
                "projet_id": str(project.pk),
                "projet_nom": project.name,
                "zones": project_zones,
                "observations": observations,
                "recommandations": recommendations,
                "prevision": forecast,
            })

        priority_list = list(priority.order_by("-score_vulnerabilite", "created_at").values(
            "id", "nom", "prenom", "score_vulnerabilite", "statut", "zone_id", "zone__nom",
            "zone__region__nom", "latitude", "longitude", "campagne_id", "campagne__nom"
        )[:10])
        aided_priority_ids = {str(value) for value in priority.filter(pk__in=aided_ids).values_list("pk", flat=True)}
        for row in priority_list:
            row["id"] = str(row["id"])
            row["zone_id"] = str(row["zone_id"])
            row["campagne_id"] = str(row["campagne_id"])
            row["score_vulnerabilite"] = float(row["score_vulnerabilite"])
            row["latitude"] = float(row["latitude"]) if row["latitude"] is not None else None
            row["longitude"] = float(row["longitude"]) if row["longitude"] is not None else None
            row["pris_en_charge"] = row["id"] in aided_priority_ids

        map_rows = list(beneficiaries.filter(latitude__isnull=False, longitude__isnull=False).values(
            "id", "latitude", "longitude", "prenom", "nom", "score_vulnerabilite", "statut", "zone__nom", "zone__region__nom", "campagne__nom"
        )[:1000])
        map_ids = [row["id"] for row in map_rows]
        need_responses = FormResponse.objects.filter(
            beneficiary_id__in=map_ids,
        ).filter(Q(question__label__icontains="besoin") | Q(question__label__icontains="aide souhaitee") | Q(question__label__icontains="assistance")).values(
            "beneficiary_id", "value_text", "value_json", "value_number", "question__label"
        ).order_by("question__ordre")
        needs_by_beneficiary = {}
        for response in need_responses:
            response_value = response["value_text"] or response["value_json"] or response["value_number"]
            if response_value and str(response["beneficiary_id"]) not in needs_by_beneficiary:
                needs_by_beneficiary[str(response["beneficiary_id"])] = str(response_value)
        map_points = []
        for row in map_rows:
            score = float(row["score_vulnerabilite"]) if row["score_vulnerabilite"] is not None else None
            priority_label = "Critique" if score is not None and score >= 80 else "Elevee" if score is not None and score >= 60 else "Moyenne" if score is not None and score >= 40 else "Faible" if score is not None else "Non evaluee"
            map_points.append({"id": str(row["id"]), "lat": float(row["latitude"]), "lng": float(row["longitude"]),
                               "nom": f'{row["prenom"]} {row["nom"]}', "score": score, "priorite": priority_label,
                               "besoin_principal": needs_by_beneficiary.get(str(row["id"])),
                               "statut": row["statut"], "zone": row["zone__nom"], "region": row["zone__region__nom"], "campagne": row["campagne__nom"]})
        map_zone_query = zones.filter(pk=zone_id) if zone_id else zones
        map_zone_query = map_zone_query.filter(latitude__isnull=False, longitude__isnull=False)
        zone_map_stats = {
            str(row["zone_id"]): row
            for row in beneficiaries.values("zone_id").annotate(
                total=Count("id"),
                prioritaires=Count("id", filter=Q(score_vulnerabilite__gte=60)),
                score_moyen=Avg("score_vulnerabilite"),
            )
        }
        map_zones = []
        for row in map_zone_query.values("id", "nom", "latitude", "longitude", "rayon", "region__nom"):
            stats = zone_map_stats.get(str(row["id"]), {})
            average_score = stats.get("score_moyen")
            map_zones.append({
                "id": str(row["id"]), "nom": row["nom"], "lat": float(row["latitude"]),
                "lng": float(row["longitude"]), "rayon": row["rayon"], "region": row["region__nom"],
                "total_beneficiaires": stats.get("total", 0),
                "beneficiaires_prioritaires": stats.get("prioritaires", 0),
                "score_moyen": round(float(average_score), 1) if average_score is not None else None,
            })

        activities = []
        for row in beneficiaries.order_by("-created_at").values("id", "created_at", "created_by__first_name", "created_by__last_name", "campagne__nom")[:8]:
            activities.append({"id": f'beneficiary-{row["id"]}', "label": "Beneficiaire enregistre", "detail": row["campagne__nom"], "at": row["created_at"].isoformat(), "actor": f'{row["created_by__first_name"] or ""} {row["created_by__last_name"] or ""}'.strip()})
        campaign_activities = campaigns
        if start_date:
            campaign_activities = campaign_activities.filter(created_at__date__gte=start_date)
        if end_date:
            campaign_activities = campaign_activities.filter(created_at__date__lte=end_date)
        for row in campaign_activities.order_by("-created_at").values("id", "created_at", "created_by__first_name", "created_by__last_name", "nom")[:8]:
            activities.append({"id": f'campaign-{row["id"]}', "label": "Campagne creee", "detail": row["nom"], "at": row["created_at"].isoformat(), "actor": f'{row["created_by__first_name"] or ""} {row["created_by__last_name"] or ""}'.strip()})
        action_rows = HumanitarianAction.objects.filter(beneficiary__in=beneficiaries)
        if start_date:
            action_rows = action_rows.filter(created_at__date__gte=start_date)
        if end_date:
            action_rows = action_rows.filter(created_at__date__lte=end_date)
        for row in action_rows.order_by("-created_at").values("id", "created_at", "agent__first_name", "agent__last_name", "type_aide", "beneficiary__prenom", "beneficiary__nom")[:8]:
            activities.append({"id": f'action-{row["id"]}', "label": "Aide humanitaire enregistree", "detail": f'{row["type_aide"]} - {row["beneficiary__prenom"]} {row["beneficiary__nom"]}', "at": row["created_at"].isoformat(), "actor": f'{row["agent__first_name"] or ""} {row["agent__last_name"] or ""}'.strip()})
        for row in expenses.order_by("-created_at").values("id", "created_at", "created_by__first_name", "created_by__last_name", "reference", "montant")[:8]:
            activities.append({"id": f'expense-{row["id"]}', "label": "Depense validee", "detail": f'{row["reference"]} - {row["montant"]} FCFA', "at": row["created_at"].isoformat(), "actor": f'{row["created_by__first_name"] or ""} {row["created_by__last_name"] or ""}'.strip()})
        activities.sort(key=lambda row: row["at"], reverse=True)

        completed = campaigns.filter(statut=Campaign.Statut.TERMINE).count()
        campaign_rate = round(completed / campaigns.count() * 100, 1) if campaigns.exists() else 0
        project_status_chart = [
            {"label": "Planifiés", "total": sum(1 for project in projects if project.start_date > today)},
            {"label": "En cours", "total": sum(1 for project in projects if project.start_date <= today <= project.end_date)},
            {"label": "Terminés", "total": sum(1 for project in projects if project.end_date < today)},
        ]
        alerts = []
        if finance["solde"] < 0:
            alerts.append({"niveau": "error", "code": "SOLDE_NEGATIF", "message": "Les depenses validees depassent les fonds recus."})
        if finance["budget_total"] and finance["taux_execution"] >= 100:
            alerts.append({"niveau": "error", "code": "BUDGET_EPUISE", "message": "Les depenses validees ont atteint ou depasse le budget."})
        if campaigns_late:
            alerts.append({"niveau": "warning", "code": "CAMPAGNES_EN_RETARD", "message": f"{campaigns_late} campagne(s) ont depasse leur date de fin."})
        if priority_unassisted:
            alerts.append({"niveau": "warning", "code": "PRIORITAIRES_NON_AIDES", "message": f"{priority_unassisted} beneficiaire(s) prioritaires sont sans aide enregistree."})
        if finance["budget_total"] and finance["taux_execution"] >= 80:
            alerts.append({"niveau": "warning", "code": "EXECUTION_BUDGETAIRE", "message": f"Le budget atteint {finance['taux_execution']} % d'execution."})

        priority_by_zone = list(priority.values("zone__nom").annotate(total=Count("id")).order_by("-total"))
        main_zone = priority_by_zone[0] if priority_by_zone else None
        insights = []
        if beneficiaries_count:
            insights.append(f"{beneficiaries_count} beneficiaire(s) dans le perimetre; {priority_count} sont prioritaires.")
        high_count = priority.filter(score_vulnerabilite__gte=90).count()
        if high_count:
            insights.append(f"{high_count} beneficiaire(s) ont un score de vulnerabilite superieur ou egal a 90.")
        if main_zone:
            insights.append(f"La zone {main_zone['zone__nom']} concentre le plus de beneficiaires prioritaires.")
        recommendations = []
        if main_zone and priority_unassisted:
            recommendations.append(f"Examiner les besoins non couverts dans la zone {main_zone['zone__nom']}.")
        if high_count:
            recommendations.append("Verifier les dossiers dont le score de vulnerabilite atteint 90 ou plus.")

        if user.role == "FINANCE":
            finance_alert_codes = {"SOLDE_NEGATIF", "BUDGET_EPUISE", "EXECUTION_BUDGETAIRE"}
            return Response({
                "finance": finance,
                "operationnel": {
                    "projets": len(projects),
                    "campagnes": campaigns.count(),
                    "campagnes_en_cours": campaigns.filter(statut=Campaign.Statut.EN_COURS).count(),
                },
                "alertes": [alert for alert in alerts if alert["code"] in finance_alert_codes],
                "filtres": {
                    "projets": project_choices,
                    "campagnes": campaign_choices,
                    "selection": {
                        "project_id": str(project_id) if project_id else "",
                        "campaign_id": campaign_id or "",
                        "start_date": start_date.isoformat() if start_date else "",
                        "end_date": end_date.isoformat() if end_date else "",
                    },
                },
                "graphiques": {
                    "finances_mensuelles": finance_series,
                    "campagnes_statuts": campaign_stats,
                },
            })

        team_summary = None
        strengths = []
        if user.role == "GERANT":
            from apps.accounts.models import User

            team = User.objects.filter(organization_id=user.organization_id)
            role_counts = {
                row["role"]: row["total"]
                for row in team.values("role").annotate(total=Count("id"))
            }
            team_summary = {
                "total": team.count(),
                "par_role": role_counts,
                "recents": list(
                    team.order_by("-date_joined", "-pk").values(
                        "id", "first_name", "last_name", "role", "status", "date_joined"
                    )[:6]
                ),
            }
            active_project_count = sum(1 for project in projects if project.start_date <= today <= project.end_date)
            active_campaign_count = campaigns.filter(statut=Campaign.Statut.EN_COURS).count()
            if active_project_count:
                strengths.append(f"{active_project_count} projet(s) sont actuellement en cours.")
            if active_campaign_count:
                strengths.append(f"{active_campaign_count} campagne(s) sont actuellement actives.")
            if aided_count:
                strengths.append(f"{aided_count} bénéficiaire(s) ont une prise en charge enregistrée.")
            if finance["financements_recus"] > 0 or finance["dons_recus"] > 0:
                strengths.append("Des financements ou des dons sont enregistrés pour l’organisation.")

        return Response({
            "finance": finance,
            "beneficiaires_par_niveau": beneficiary_levels,
            "operationnel": {
                "projets": len(projects),
                "projets_actifs": sum(1 for project in projects if project.start_date <= today <= project.end_date),
                "campagnes": campaigns.count(),
                "campagnes_en_cours": campaigns.filter(statut=Campaign.Statut.EN_COURS).count(),
                "campagnes_en_retard": campaigns_late, "beneficiaires": beneficiaries_count,
                "beneficiaires_prioritaires": priority_status_count, "beneficiaires_aides": aided_count,
                "beneficiaires_prioritaires_non_aides": priority_unassisted,
                "taux_couverture": round(priority_aided / priority_count * 100, 1) if priority_count else 0,
                "taux_prise_en_charge": round(taken_care_status_count / beneficiaries_count * 100, 1) if beneficiaries_count else 0,
                "taux_realisation_campagnes": campaign_rate, "progression_projets": campaign_rate,
                "anomalies_sync": beneficiaries.filter(sync_status__in=["FAILED", "DUPLICATE"]).count(),
            },
            "alertes": alerts,
            "filtres": {
                "projets": project_choices, "campagnes": campaign_choices,
                "regions": [{"id": row["region_id"], "nom": row["region__nom"]} for row in region_choices],
                "zones": [{"id": str(row["id"]), "nom": row["nom"], "region_id": row["region_id"], "region": row["region__nom"]} for row in zone_choices],
                "selection": {"project_id": str(project_id) if project_id else "", "campaign_id": campaign_id or "", "region_id": str(region_id) if region_id else "", "zone_id": zone_id or "", "start_date": start_date.isoformat() if start_date else "", "end_date": end_date.isoformat() if end_date else ""},
            },
            "graphiques": {"beneficiaires_mensuels": monthly_series, "finances_mensuelles": finance_series, "campagnes_statuts": campaign_stats, "campagnes_chart": campaigns_chart, "beneficiaires_zones": zone_stats, "projets_statuts": project_status_chart},
            "utilisateurs": team_summary,
            "points_forts": strengths if user.role == "GERANT" else None,
            "zones_prioritaires_par_projet": project_zone_analysis,
            "carte": {"points": map_points, "zones": map_zones},
            "beneficiaires_prioritaires": priority_list,
            "activites_recentes": activities[:12],
            "analyse_operationnelle": insights,
            "recommandations": recommendations,
        })


class ProjectDashboardAssistantChatView(APIView):
    """Chat uses a filtered, aggregate-only context from the project dashboard."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        question = (request.data.get("question") or "").strip()
        if not user.can_login or user.role != "CHEF_PROJET":
            return Response({"detail": "Assistant reserve au Chef de projet."}, status=status.HTTP_403_FORBIDDEN)
        if not question or len(question) > 4000:
            return Response({"detail": "La question doit contenir entre 1 et 4000 caracteres."}, status=status.HTTP_400_BAD_REQUEST)

        dashboard_response = ProjectDecisionDashboardView().get(request)
        if dashboard_response.status_code >= 400:
            return dashboard_response
        dashboard = dashboard_response.data
        context = {
            "role": "CHEF_PROJET",
            "filtres": dashboard["filtres"]["selection"],
            "operationnel": dashboard["operationnel"],
            "finances": dashboard["finance"],
            "alertes": dashboard["alertes"],
            "beneficiaires_par_mois": dashboard["graphiques"]["beneficiaires_mensuels"],
            "finances_par_mois": dashboard["graphiques"]["finances_mensuelles"],
            "campagnes_par_statut": dashboard["graphiques"]["campagnes_statuts"],
            "beneficiaires_par_zone": dashboard["graphiques"]["beneficiaires_zones"],
            "observations": dashboard["analyse_operationnelle"],
            "recommandations_existantes": dashboard["recommandations"],
        }
        payload = {"tenant": ai_tenant_identity(user), "question": question, "context": context}
        try:
            result = post_to_ai_service(
                f"{settings.IA_SERVICE_URL.rstrip('/')}/api/ia/chat",
                payload=payload,
                timeout=30,
            )
            result.raise_for_status()
            return Response(result.json())
        except requests.RequestException:
            return Response({"detail": "Le service IA est temporairement indisponible."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class ProjectCampaignProposalView(APIView):
    """Return reviewable campaign proposals; this endpoint never creates campaigns."""

    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        user = request.user
        if not user.can_login or user.role != "CHEF_PROJET":
            return Response({"detail": "Réservé au Chef de projet."}, status=status.HTTP_403_FORBIDDEN)

        project = Project.objects.filter(
            pk=project_id,
            chef_projet=user,
            organization=user.organization,
            archived=False,
        ).first()
        if not project:
            return Response({"detail": "Projet introuvable dans votre périmètre."}, status=status.HTTP_404_NOT_FOUND)

        today = timezone.localdate()
        if project.end_date < today:
            return Response({"detail": "La date de fin du projet est passée; aucune campagne ne peut être proposée dans sa période."}, status=status.HTTP_400_BAD_REQUEST)

        project_campaigns = Campaign.objects.filter(projet=project, organization=user.organization)
        beneficiary_base = Beneficiary.objects.filter(
            campagne__in=project_campaigns,
            organization=user.organization,
        )
        beneficiary_count = beneficiary_base.count()
        priority_count = beneficiary_base.filter(score_vulnerabilite__gte=60).count()
        zone_rows = list(
            Zone.objects.filter(
                organization=user.organization,
                statut=True,
            ).filter(
                Q(region__nom__iexact=project.region)
                | Q(campaigns__projet=project, campaigns__organization=user.organization)
            ).values("id", "nom", "region__nom").distinct().order_by("nom")
        )
        # Fallback: if no zones match the project region/campaigns, expose all active
        # org zones so the AI can still generate meaningful proposals.
        if not zone_rows:
            zone_rows = list(
                Zone.objects.filter(
                    organization=user.organization,
                    statut=True,
                ).values("id", "nom", "region__nom").distinct().order_by("nom")
            )
        allowed_zone_ids = {str(row["id"]) for row in zone_rows}
        def normalize_choice(value):
            value = unicodedata.normalize("NFD", str(value or "").strip().lower())
            value = "".join(char for char in value if unicodedata.category(char) != "Mn")
            return re.sub(r"[^a-z0-9]+", "_", value).strip("_")

        allowed_zone_names = {normalize_choice(row["nom"]): str(row["id"]) for row in zone_rows}
        campaign_rows = list(project_campaigns.order_by("-created_at").values("nom", "type", "statut", "date_debut", "date_fin")[:20])
        project_budget = Budget.objects.filter(
            projet=project,
            organization=user.organization,
        ).aggregate(total=Sum("montant"))["total"] or 0
        project_criteria = list(
            ProjectCriteria.objects.filter(projet=project, actif=True)
            .values("nom", "poids", "question__label", "vulnerable_values", "vulnerable_operator")
            .order_by("nom")
        )
        for campaign in campaign_rows:
            campaign["date_debut"] = campaign["date_debut"].isoformat()
            campaign["date_fin"] = campaign["date_fin"].isoformat()

        project_context = {
            "projet": {
                "nom": project.name,
                "code": project.code,
                "description": project.description,
                "objectif": project.objectif,
                "region": project.region,
                "budget_fcfa": str(project_budget),
                "date_debut": project.start_date.isoformat(),
                "date_fin": project.end_date.isoformat(),
            },
            "date_du_jour": today.isoformat(),
            "beneficiaires": {"total": beneficiary_count, "prioritaires_score_60_plus": priority_count},
            "criteres_du_projet": project_criteria,
            "campagnes_existantes": campaign_rows,
            "zones_autorisees": [
                {"id": str(row["id"]), "nom": row["nom"], "region": row["region__nom"]}
                for row in zone_rows
            ],
            "types_autorises": [value for value, _label in Campaign.Type.choices if value != Campaign.Type.COLLECTE],
        }
        question = (
            "Analyse ce projet en tenant compte en priorité de ses critères de vulnérabilité, de leurs poids et des réponses associées. "
            "Explique brièvement comment les critères orientent le résumé et les campagnes proposées. "
            "Propose au maximum 3 campagnes utiles et complémentaires. "
            "Réponds uniquement en JSON valide, sans Markdown, selon ce schéma: "
            '{"analyse":"...","propositions":[{"nom":"...","type":"...","description":"...",'
            '"date_debut":"YYYY-MM-DD","date_fin":"YYYY-MM-DD","zone_ids":["..."],"justification":"..."}]}. '
            "Utilise uniquement les types et identifiants de zones autorisés dans le contexte. "
            "Les dates doivent être futures ou égales à aujourd'hui, comprises dans la période du projet, "
            "et la date de fin doit suivre la date de début. N'invente aucun chiffre ni zone. "
            "Les propositions sont soumises à décision humaine; ne prétends pas les créer."
        )
        question += (
            " Return only valid JSON. For each proposal, copy an exact allowed campaign type code and the exact zone UUIDs "
            "from the context in zone_ids as an array of strings; do not return zone names instead of IDs."
        )
        try:
            ai_response = post_to_ai_service(
                f"{settings.IA_SERVICE_URL.rstrip('/')}/api/ia/chat",
                payload={"tenant": ai_tenant_identity(user), "question": question, "context": project_context},
                timeout=45,
            )
            ai_response.raise_for_status()
            answer = ai_response.json().get("answer", "")
            json_match = re.search(r"\{.*\}", answer, flags=re.DOTALL)
            if not json_match:
                raise ValueError("La réponse IA ne contient pas de proposition structurée.")
            generated = json.loads(json_match.group(0))
            analysis = str(generated.get("analyse") or generated.get("analysis") or "").strip()
            proposals = []
            valid_types = {value for value, _label in Campaign.Type.choices if value != Campaign.Type.COLLECTE}
            type_aliases = {normalize_choice(label): value for value, label in Campaign.Type.choices if value != Campaign.Type.COLLECTE}
            type_aliases.update({normalize_choice(value): value for value in valid_types})
            raw_proposals = generated.get("propositions", generated.get("proposals", []))
            if not isinstance(raw_proposals, list):
                raw_proposals = []
            for proposal in raw_proposals[:3]:
                if not isinstance(proposal, dict):
                    continue
                kind_raw = proposal.get("type")
                kind = type_aliases.get(normalize_choice(kind_raw), kind_raw)
                raw_zones = proposal.get("zone_ids", proposal.get("zones", []))
                if not isinstance(raw_zones, list):
                    raw_zones = [raw_zones]
                selected_zones = []
                for value in raw_zones:
                    zone_id = str(value.get("id", "")) if isinstance(value, dict) else str(value)
                    if zone_id not in allowed_zone_ids:
                        zone_name = value.get("nom", value.get("name", "")) if isinstance(value, dict) else value
                        zone_id = allowed_zone_names.get(normalize_choice(zone_name), "")
                    if zone_id and zone_id not in selected_zones:
                        selected_zones.append(zone_id)
                try:
                    starts_raw = proposal.get("date_debut") or proposal.get("date_start") or ""
                    ends_raw = proposal.get("date_fin") or proposal.get("date_end") or ""
                    starts = date.fromisoformat(str(starts_raw)[:10])
                    ends = date.fromisoformat(str(ends_raw)[:10])
                except (TypeError, ValueError):
                    continue
                if (
                    kind not in valid_types
                    or not selected_zones
                    or starts < today
                    or starts < project.start_date
                    or ends > project.end_date
                    or ends < starts
                ):
                    continue
                proposals.append({
                    "nom": str(proposal.get("nom", ""))[:200],
                    "type": kind,
                    "description": str(proposal.get("description", ""))[:5000],
                    "date_debut": starts.isoformat(),
                    "date_fin": ends.isoformat(),
                    "zones": [row for row in project_context["zones_autorisees"] if row["id"] in selected_zones],
                    "justification": str(proposal.get("justification", ""))[:2000],
                })
            if not proposals:
                logger.warning(
                    "Campaign proposal response had no valid proposals (project_id=%s, returned=%s, allowed_zones=%s)",
                    project.pk,
                    len(raw_proposals) if isinstance(raw_proposals, list) else 0,
                    len(allowed_zone_ids),
                )
                return Response(
                    {
                        "detail": (
                            "L'IA n'a pas pu produire de proposition valide. "
                            "Vérifiez que le projet a des zones actives, des dates futures et des critères configurés, "
                            "puis réessayez."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not analysis:
                analysis = f"Propositions établies à partir des critères et de la période du projet « {project.name} »."
            return Response({"analyse": analysis, "propositions": proposals})
        except (requests.RequestException, ValueError, json.JSONDecodeError):
            return Response({"detail": "Impossible d'obtenir une proposition IA structurée pour le moment."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@extend_schema(tags=["Projets"])
class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAccountActive, IsGerantOrFinanceOrAgent, CanManageProject]
    queryset = Project.objects.select_related(
        "chef_projet", "responsable_finance", "organization", "created_by"
    ).prefetch_related("criteres").all()

    def get_queryset(self):
        queryset = scope_by_organization(self.queryset, self.request.user)
        if self.request.user.role == "CHEF_PROJET":
            queryset = queryset.filter(chef_projet=self.request.user)
        elif self.request.user.role == "FINANCE":
            queryset = queryset.filter(responsable_finance=self.request.user)
        elif self.request.user.role == "AGENT":
            queryset = queryset.filter(campaigns__affectations__agent=self.request.user).distinct()
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.archived = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["Projets"])
class ProjectBudgetView(generics.UpdateAPIView):
    serializer_class = BudgetUpdateSerializer
    permission_classes = [IsAccountActive, IsGerantOrFinanceOrAgent, CanManageProject]
    queryset = Project.objects.all()

    def get_queryset(self):
        return scope_by_organization(self.queryset, self.request.user)

    def get_object(self):
        obj = super().get_object()
        if self.request.user.role not in ["GERANT", "FINANCE", "SUPER_ADMIN"]:
            self.permission_denied(self.request)
        return obj

    def update(self, request, *args, **kwargs):
        project = self.get_object()
        serializer = self.get_serializer(project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        project_serializer = ProjectSerializer(
            project,
            data={"budget": serializer.validated_data["budget"]},
            partial=True,
            context=self.get_serializer_context(),
        )
        project_serializer.is_valid(raise_exception=True)
        project_serializer.save()
        return Response(project_serializer.data)


@extend_schema(tags=["Critères Projet"])
class ProjectCriteriaListView(generics.ListCreateAPIView):
    serializer_class = ProjectCriteriaSerializer
    permission_classes = [IsAccountActive, IsGerantOrFinanceOrAgent]
    queryset = ProjectCriteria.objects.select_related("created_by", "projet").all()

    def get_queryset(self):
        projet_id = self.kwargs.get("project_id")
        return scope_by_organization(
            self.queryset.filter(projet_id=projet_id, actif=True),
            self.request.user,
            lookup="projet__organization",
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProjectCriteriaCreateSerializer
        return ProjectCriteriaSerializer

    def list(self, request, *args, **kwargs):
        projet_id = kwargs.get("project_id")
        projet = scope_by_organization(
            Project.objects.filter(pk=projet_id), request.user
        ).first()
        if not projet:
            return Response({"detail": "Projet introuvable."}, status=status.HTTP_404_NOT_FOUND)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        total_poids = sum(c.poids for c in queryset)
        return Response({
            "total_poids": total_poids,
            "criteres": serializer.data,
        })

    def create(self, request, *args, **kwargs):
        projet_id = kwargs.get("project_id")
        projet = scope_by_organization(
            Project.objects.filter(pk=projet_id), request.user
        ).first()
        if not projet:
            return Response({"detail": "Projet introuvable."}, status=status.HTTP_404_NOT_FOUND)
        if request.user.role not in ["GERANT", "CHEF_PROJET", "SUPER_ADMIN"]:
            return Response(
                {"detail": "Vous n'êtes pas autorisé à modifier les critères de ce projet."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if request.user.role == "CHEF_PROJET" and projet.chef_projet != request.user:
            return Response(
                {"detail": "Vous n'êtes pas chef de ce projet."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data, context={"projet": projet, "request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Critères Projet"])
class ProjectCriteriaDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectCriteriaSerializer
    permission_classes = [IsAccountActive, IsGerantOrFinanceOrAgent, CanManageProjectCriteria]
    queryset = ProjectCriteria.objects.select_related("created_by", "projet").all()

    def get_queryset(self):
        return scope_by_organization(
            self.queryset.filter(actif=True),
            self.request.user,
            lookup="projet__organization",
        )

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return ProjectCriteriaCreateSerializer
        return ProjectCriteriaSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.actif = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
