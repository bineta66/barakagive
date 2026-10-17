import json
import logging
import requests
import unicodedata
import uuid
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser

from apps.campaigns.models import Campaign
from apps.campaigns.models import CampagneAffectation
from apps.beneficiaries.models import Beneficiary, HumanitarianAction
from apps.zones.models import Zone
from apps.finance.models import Depense, Budget
from apps.projects.models import Project
from apps.ia.models import IAnalyse, AssistantInteraction
from apps.accounts.models import InAppNotification
from apps.accounts.permissions import IsAccountActive
from apps.ia.services import compute_region_zones_data, get_zone_beneficiaries_detail
from apps.common.interservice import post_to_ai_service, ai_tenant_identity
from apps.ia.guardrails import input_guardrail_message, out_of_scope_message, safe_audit_text
from apps.ia.project_creation import handle_project_creation
from apps.ia.assistant_intents import classify_assistant_intent

logger = logging.getLogger(__name__)


# Matrice IA basée sur User.Role et les relations présentes dans les modèles.
# GERANT: synthèse de son ONG; CHEF_PROJET: projets dont il est responsable;
# FINANCE: finances de son ONG; AGENT: uniquement campagnes/zones affectées;
# SUPER_ADMIN: périmètre global.
IA_DASHBOARD_ROLES = {"GERANT", "SUPER_ADMIN"}
IA_ANALYSIS_ROLES = {"GERANT", "CHEF_PROJET", "SUPER_ADMIN"}


def campaigns_for_user(user):
    """Campagnes IA visibles selon le rôle et les affectations métier."""
    campaigns = Campaign.objects.select_related("projet", "organization")
    if user.role == "SUPER_ADMIN":
        return campaigns
    if not user.organization_id:
        return campaigns.none()
    campaigns = campaigns.filter(
        organization_id=user.organization_id,
        projet__organization_id=user.organization_id,
    )
    if user.role == "CHEF_PROJET":
        return campaigns.filter(projet__chef_projet=user)
    if user.role == "FINANCE":
        return campaigns.filter(projet__responsable_finance=user)
    if user.role == "AGENT":
        return campaigns.filter(affectations__agent=user).distinct()
    if user.role == "GERANT":
        return campaigns
    return campaigns.none()


def get_active_campaign(user):
    """Dernière campagne en cours dans le périmètre de l'utilisateur."""
    return campaigns_for_user(user).filter(
        statut=Campaign.Statut.EN_COURS,
        projet__archived=False,
    ).order_by("-date_debut", "-created_at").first()


def zone_is_visible_to_user(user, campaign, zone):
    if not campaign.zones.filter(pk=zone.pk).exists():
        return False
    if user.role != "AGENT":
        return True
    # L'affectation référence le nom de zone (champ texte) dans le schéma actuel.
    return CampagneAffectation.objects.filter(
        campagne=campaign, agent=user, zone=zone.nom,
    ).exists()


def compute_assistant_dashboard(user):
    """
    Calcule dynamiquement les métriques exécutives réelles de l'organisation à partir de PostgreSQL.
    Aucune donnée n'est simulée ou codée en dur.
    """
    now = timezone.now()
    today = now.date()

    if user.role == "SUPER_ADMIN":
        projects_qs = Project.objects.all()
        campaigns_qs = Campaign.objects.all()
        beneficiaries_qs = Beneficiary.objects.all()
        budgets_qs = Budget.objects.all()
        depenses_qs = Depense.objects.all()
    elif user.role == "GERANT":
        if not user.organization_id:
            projects_qs = Project.objects.none()
            campaigns_qs = Campaign.objects.none()
            beneficiaries_qs = Beneficiary.objects.none()
            budgets_qs = Budget.objects.none()
            depenses_qs = Depense.objects.none()
        else:
            org = user.organization
            projects_qs = Project.objects.filter(organization=org)
            campaigns_qs = Campaign.objects.filter(organization=org)
            beneficiaries_qs = Beneficiary.objects.filter(organization=org)
            budgets_qs = Budget.objects.filter(organization=org)
            depenses_qs = Depense.objects.filter(organization=org)
    elif user.role == "CHEF_PROJET":
        projects_qs = Project.objects.filter(organization_id=user.organization_id, chef_projet=user) if user.organization_id else Project.objects.none()
        campaigns_qs = Campaign.objects.filter(
            organization=user.organization, projet__chef_projet=user,
        )
        beneficiaries_qs = Beneficiary.objects.filter(
            organization=user.organization, campagne__in=campaigns_qs,
        )
        budgets_qs = Budget.objects.filter(organization=user.organization, projet__in=projects_qs)
        depenses_qs = Depense.objects.filter(organization=user.organization, projet__in=projects_qs)
    elif user.role == "FINANCE":
        projects_qs = Project.objects.filter(organization_id=user.organization_id, responsable_finance=user) if user.organization_id else Project.objects.none()
        campaigns_qs = Campaign.objects.filter(organization=user.organization, projet__in=projects_qs)
        beneficiaries_qs = Beneficiary.objects.none()
        budgets_qs = Budget.objects.filter(organization=user.organization, projet__in=projects_qs)
        depenses_qs = Depense.objects.filter(organization=user.organization, projet__in=projects_qs)
    else:
        projects_qs = Project.objects.none()
        campaigns_qs = Campaign.objects.none()
        beneficiaries_qs = Beneficiary.objects.none()
        budgets_qs = Budget.objects.none()
        depenses_qs = Depense.objects.none()

    # 1. Projets et Campagnes actifs
    projets_actifs = projects_qs.filter(archived=False).count()
    active_campaigns_qs = campaigns_qs.filter(statut=Campaign.Statut.EN_COURS)
    campagnes_actives = active_campaigns_qs.count()
    beneficiaires = beneficiaries_qs.count()

    # 2. Données Financières
    sum_budgets = budgets_qs.aggregate(total=models.Sum("montant"))["total"]
    if sum_budgets is None or sum_budgets == 0:
        sum_prj_budgets = projects_qs.filter(archived=False).aggregate(total=models.Sum("budget"))["total"]
        budget_total = float(sum_prj_budgets or 0)
    else:
        budget_total = float(sum_budgets or 0)

    sum_depenses = depenses_qs.aggregate(total=models.Sum("montant"))["total"]
    depenses = float(sum_depenses or 0)
    solde = budget_total - depenses
    taux_execution = (depenses / budget_total * 100) if budget_total > 0 else 0

    # 3. Campagnes proches de la clôture (date_fin >= aujourd'hui)
    closing_soon_campaigns = list(
        active_campaigns_qs.filter(date_fin__gte=today).order_by("date_fin")[:5]
    )

    # 4. Régions les plus actives
    region_counts = (
        beneficiaries_qs.values("zone__region")
        .annotate(total=models.Count("id"))
        .order_by("-total")
    )
    region_counts = [r for r in region_counts if r.get("zone__region")]
    top_region = region_counts[0]["zone__region"] if region_counts else None
    top_region_count = region_counts[0]["total"] if region_counts else 0

    # 5. Campagne avec le plus de bénéficiaires
    top_campaign = None
    if active_campaigns_qs.exists():
        top_campaign = (
            active_campaigns_qs.annotate(nb_ben=models.Count("beneficiaries"))
            .order_by("-nb_ben")
            .first()
        )

    # 6. Résumé dynamique
    if campagnes_actives > 0:
        if top_campaign and top_campaign.beneficiaries.count() > 0:
            camp_plural = "campagnes sont actuellement en cours" if campagnes_actives > 1 else "campagne est actuellement en cours"
            resume = (
                f"{campagnes_actives} {camp_plural}. "
                f"La campagne '{top_campaign.nom}' présente le plus grand nombre de bénéficiaires ({top_campaign.beneficiaries.count()})."
            )
        else:
            camp_plural = "campagnes sont actuellement en cours" if campagnes_actives > 1 else "campagne est actuellement en cours"
            ben_plural = "bénéficiaires enregistrés" if beneficiaires > 1 else "bénéficiaire enregistré"
            resume = f"{campagnes_actives} {camp_plural} avec {beneficiaires} {ben_plural}."
    elif projets_actifs > 0:
        prj_plural = "projets actifs" if projets_actifs > 1 else "projet actif"
        resume = f"{projets_actifs} {prj_plural}. Aucune campagne opérationnelle n'est actuellement en cours."
    else:
        resume = "Aucun projet ou campagne active n'est actuellement enregistré."

    # 7. Alertes réelles calculées
    alertes = []

    # Projets dépassant 80% du budget
    high_budget_projects = []
    for p in projects_qs.filter(archived=False).prefetch_related("budgets"):
        p_budget = float(p.budgets.aggregate(s=models.Sum("montant"))["s"] or 0)
        if p_budget > 0:
            p_dep = float(depenses_qs.filter(projet=p).aggregate(s=models.Sum("montant"))["s"] or 0)
            ratio = (p_dep / p_budget) * 100
            if ratio >= 80:
                high_budget_projects.append((p.name, round(ratio, 1)))

    if len(high_budget_projects) == 1:
        alertes.append(f"Le projet '{high_budget_projects[0][0]}' dépasse {high_budget_projects[0][1]} % de son budget")
    elif len(high_budget_projects) > 1:
        alertes.append(f"{len(high_budget_projects)} projets dépassent 80 % de leur enveloppe budgétaire")

    # Concentration géographique
    if top_region and beneficiaires > 0:
        pct_region = round((top_region_count / beneficiaires) * 100)
        if pct_region >= 30:
            alertes.append(f"La région de {top_region} concentre le plus de bénéficiaires ({top_region_count} bénéficiaires, soit {pct_region} %)")

    # Campagnes proches de la clôture
    for camp in closing_soon_campaigns:
        days_left = (camp.date_fin - today).days
        if days_left <= 7:
            days_label = "aujourd'hui" if days_left == 0 else f"dans {days_left} jour{'s' if days_left > 1 else ''}"
            alertes.append(f"La campagne '{camp.nom}' se clôture {days_label}")

    # Solde déficitaire ou critique
    if solde < 0:
        alertes.append("Le solde budgétaire global présente un dépassement (déficit).")
    elif budget_total > 0 and (solde / budget_total) < 0.1:
        alertes.append("Le solde budgétaire disponible restant est inférieur à 10 %.")

    if not alertes:
        alertes.append("Aucune anomalie budgétaire ou opérationnelle détectée.")

    # 8. Recommandations dynamiques
    recommandations = []
    if closing_soon_campaigns:
        camp_names = ", ".join([c.nom for c in closing_soon_campaigns[:2]])
        recommandations.append(f"Prioriser les campagnes proches de la clôture ({camp_names})")

    if high_budget_projects:
        recommandations.append("Vérifier et ajuster les dépenses des projets à risque budgétaire élevé")

    if beneficiaires == 0 and campagnes_actives > 0:
        recommandations.append("Mobiliser les agents terrain pour accélérer le recensement des bénéficiaires")

    if solde > 0 and taux_execution < 50 and campagnes_actives > 0:
        recommandations.append("Accélérer l'exécution des activités planifiées pour atteindre les objectifs de décaissement")

    recommandations.append("Consulter la carte des priorités pour orienter les actions vers les zones les plus vulnérables")

    # Alerte status pour indicateur orb (GREEN, YELLOW, RED)
    alert_status = "GREEN"
    if high_budget_projects or solde < 0:
        alert_status = "RED"
    elif any((camp.date_fin - today).days <= 7 for camp in closing_soon_campaigns) or (budget_total > 0 and (solde / budget_total) < 0.1):
        alert_status = "YELLOW"

    return {
        "generated_at": now.isoformat(),
        "projets_actifs": projets_actifs,
        "campagnes_actives": campagnes_actives,
        "beneficiaires": beneficiaires,
        "budget_total": budget_total,
        "depenses": depenses,
        "solde": solde,
        "taux_execution": round(taux_execution, 1),
        "resume": resume,
        "alertes": alertes,
        "recommandations": recommandations[:4],
        "alert": alert_status,
        "budget": {
            "total": budget_total,
            "depenses": depenses,
            "solde": solde,
            "taux": round(taux_execution, 1),
            "alerte": alert_status == "RED",
        },
        "campagne_prioritaire": {
            "nom": top_campaign.nom,
            "urgence": "Élevée" if (top_campaign.date_fin - today).days <= 14 else "Normale",
            "region": top_campaign.zones.first().region.nom if top_campaign and top_campaign.zones.exists() else "Multi-zones",
        } if top_campaign else None,
    }


class AssistantDashboardView(APIView):
    """
    GET /api/assistant/dashboard/
    Retourne les indicateurs stratégiques et opérationnels en temps réel
    calculés exclusivement depuis la base de données PostgreSQL.
    """
    permission_classes = [IsAuthenticated, IsAccountActive]

    def get(self, request):
        if request.user.role not in IA_DASHBOARD_ROLES | {"CHEF_PROJET", "FINANCE"}:
            return Response({"detail": "Accès refusé pour ce rôle."}, status=403)
        data = compute_assistant_dashboard(request.user)
        return Response(data)


def compute_executive_payload(campaign, user):
    """Compute executive insight payload from Django data"""
    # Beneficiaries stats
    beneficiaries = Beneficiary.objects.filter(
        campagne=campaign,
        organization_id=campaign.organization_id,
        campagne__projet__organization_id=campaign.organization_id,
        zone__organization_id=campaign.organization_id,
    )
    total_beneficiaries = beneficiaries.count()
    
    # Zones with beneficiary counts and scores
    zones = Zone.objects.filter(campaigns=campaign, organization=user.organization)
    zones_data = []
    for zone in zones:
        zone_beneficiaries = beneficiaries.filter(zone=zone)
        avg_score = zone_beneficiaries.exclude(score_vulnerabilite__isnull=True).aggregate(
            avg_score=models.Avg('score_vulnerabilite')
        )['avg_score'] or 0
        zones_data.append({
            "id": str(zone.id),
            "nom": zone.nom,
            "region": zone.region.nom if zone.region_id else "",
            "departement": zone.departement,
            "beneficiaires": zone_beneficiaries.count(),
            "score_moyen": float(avg_score),
            "latitude": float(zone.latitude),
            "longitude": float(zone.longitude),
        })
    
    # Budget data
    budgets = Budget.objects.filter(
        projet=campaign.projet, organization_id=campaign.organization_id,
    )
    total_budget = sum(float(b.montant) for b in budgets)
    
    depenses = Depense.objects.filter(
        organization_id=campaign.organization_id,
    ).filter(
        models.Q(projet=campaign.projet)
        | models.Q(budget__projet=campaign.projet)
        | models.Q(ligne_budgetaire__budget__projet=campaign.projet)
        | models.Q(campagne=campaign)
    ).distinct()
    total_depenses = sum(float(d.montant) for d in depenses)
    
    # Expenses by zone and category
    depenses_par_zone = {}
    depenses_par_categorie = {}
    for depense in depenses:
        cat_name = depense.categorie or "Non catégorisé"
        depenses_par_categorie[cat_name] = depenses_par_categorie.get(cat_name, 0) + float(depense.montant)
    
    return {
        "campagne_id": str(campaign.id),
        "nom": campaign.nom,
        "date_debut": campaign.date_debut.isoformat(),
        "date_fin": campaign.date_fin.isoformat(),
        "total_beneficiaires": total_beneficiaries,
        "zones": zones_data,
        "budgets": [
            {"id": str(b.id), "montant_total": float(b.montant), "statut": b.statut}
            for b in budgets
        ],
        "total_budget": total_budget,
        "total_depenses": total_depenses,
        "solde": total_budget - total_depenses,
        "taux_execution": (total_depenses / total_budget * 100) if total_budget > 0 else 0,
        "depenses_par_zone": depenses_par_zone,
        "depenses_par_categorie": depenses_par_categorie,
    }


def compute_finance_payload(campaign, user):
    """Compute finance payload for budget analysis"""
    budgets = Budget.objects.filter(
        projet=campaign.projet, organization_id=campaign.organization_id,
    )
    total_budget = sum(float(b.montant) for b in budgets)
    
    depenses = Depense.objects.filter(
        organization_id=campaign.organization_id,
    ).filter(
        models.Q(projet=campaign.projet)
        | models.Q(budget__projet=campaign.projet)
        | models.Q(ligne_budgetaire__budget__projet=campaign.projet)
        | models.Q(campagne=campaign)
    ).distinct()
    total_depenses = sum(float(d.montant) for d in depenses)
    solde = total_budget - total_depenses
    taux = (total_depenses / total_budget * 100) if total_budget > 0 else 0
    
    # Expenses have no direct zone relation; do not invent a zone attribution.
    depenses_par_zone = {}
    
    # Expenses by category
    depenses_par_categorie = {}
    for depense in depenses:
        cat_name = depense.categorie or "Non catégorisé"
        depenses_par_categorie[cat_name] = depenses_par_categorie.get(cat_name, 0) + float(depense.montant)
    
    return {
        "campagne_id": str(campaign.id),
        "nom": campaign.nom,
        "budget_total": total_budget,
        "depenses_totales": total_depenses,
        "solde": solde,
        "taux_execution": taux,
        "date_cloture": campaign.date_fin.isoformat(),
        "jours_restants": (campaign.date_fin - timezone.now().date()).days,
        "depenses_par_zone": depenses_par_zone,
        "depenses_par_categorie": depenses_par_categorie,
    }


def call_ia_service(endpoint: str, payload: dict) -> dict:
    """Call the FastAPI IA service"""
    url = f"{settings.IA_SERVICE_URL}{endpoint}"
    try:
        response = post_to_ai_service(url, payload=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error("IA service call failed (error_type=%s)", type(e).__name__)
        raise


class ExecutiveInsightView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.role not in IA_DASHBOARD_ROLES | {"CHEF_PROJET", "FINANCE"}:
            return Response({"detail": "Accès refusé pour ce rôle."}, status=403)
        data = compute_assistant_dashboard(request.user)
        return Response(data)


class RegionZonesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id):
        if request.user.role not in IA_ANALYSIS_ROLES | {"AGENT"}:
            return Response({"detail": "Accès refusé."}, status=403)
        campaign = get_active_campaign(request.user)
        if not campaign:
            return Response({"detail": "Aucune campagne active autorisée."}, status=404)
        
        # Donnees calculees par Django (jamais d'erreur 500 pour un cas metier)
        try:
            data = compute_region_zones_data(campaign, id)
        except Exception as e:
            logger.error("Region zones failed (error_type=%s)", type(e).__name__)
            return Response({"region": id, "zones": []})

        zones = data.get("zones", [])
        if request.user.role == "AGENT":
            assigned_names = set(CampagneAffectation.objects.filter(
                campagne=campaign, agent=request.user,
            ).values_list("zone", flat=True))
            zones = [zone for zone in zones if zone.get("nom") in assigned_names]
        return Response({
            "region": id,
            "zones": zones,
        })


class ZoneDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id):
        if request.user.role not in IA_ANALYSIS_ROLES | {"AGENT"}:
            return Response({"detail": "Accès refusé."}, status=403)
        campaign = get_active_campaign(request.user)
        if not campaign:
            return Response({"detail": "Aucune campagne active autorisée."}, status=404)

        try:
            zone = Zone.objects.get(pk=id, organization_id=campaign.organization_id)
        except (Zone.DoesNotExist, ValueError):
            zone = Zone.objects.filter(
                nom=id, organization_id=campaign.organization_id,
            ).first()
        if not zone:
            return Response({"message": "Zone non trouvée"}, status=404)
        if not zone_is_visible_to_user(request.user, campaign, zone):
            return Response({"message": "Zone non trouvée"}, status=404)

        # L'agent ne transmet jamais au service IA le contexte complet de la campagne.
        if request.user.role == "AGENT":
            return self._django_zone_detail(campaign, str(zone.pk))
        
        analysis = IAnalyse.objects.filter(
            campagne=campaign, 
            type_analyse='global'
        ).first()
        
        if analysis and analysis.response_data:
            zones = analysis.response_data.get('zones_prioritaires', [])
            for z in zones:
                if str(z.get('id', '')) == str(zone.pk) or z.get('nom') == zone.nom:
                    # Get detailed analysis
                    payload = compute_executive_payload(campaign, request.user)
                    try:
                        detail = call_ia_service(f"/api/ia/zones/{zone.pk}/analyze", payload)
                        return Response(detail)
                    except Exception as e:
                        logger.error("Zone detail failed (error_type=%s)", type(e).__name__)
                    # IA indisponible : on retombe sur les donnees calculees par Django
                    return self._django_zone_detail(campaign, str(zone.pk))
            return Response({"message": "Zone non trouvée"}, status=404)

        # Aucune analyse en cache : donnees calculees par Django
        return self._django_zone_detail(campaign, str(zone.pk))

    @staticmethod
    def _django_zone_detail(campaign, zone_id):
        """Retourne les donnees de zone calculees par Django (404 si absente)."""
        try:
            return Response(get_zone_beneficiaries_detail(campaign, zone_id))
        except (Zone.DoesNotExist, ValueError):
            return Response({"message": "Zone non trouvée"}, status=404)


class BudgetAnalysisView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, campagne_id):
        if request.user.role not in {"GERANT", "FINANCE", "SUPER_ADMIN"}:
            return Response({"detail": "Accès réservé aux responsables financiers."}, status=403)
        try:
            campaign = campaigns_for_user(request.user).get(
                id=campagne_id,
                projet__organization_id=models.F("organization_id"),
                **({"projet__responsable_finance": request.user} if request.user.role == "FINANCE" else {}),
            )
        except Campaign.DoesNotExist:
            return Response({"detail": "Campagne non trouvée ou accès refusé."}, status=404)
        
        # Do not return an old cached finance snapshot: it may have been
        # generated before financial relations were scoped by organization.
        # Build a fresh tenant-filtered payload below.
        payload = compute_finance_payload(campaign, request.user)
        try:
            result = call_ia_service(f"/api/ia/budget-analysis/{campagne_id}", payload)
            return Response(result)
        except Exception as e:
            logger.error("Budget analysis failed (%s)", type(e).__name__)
            return Response({
                "financial_data": payload,
                "ia_analysis": None,
                "message": "Le service IA est temporairement indisponible.",
                "generated_at": timezone.now().isoformat()
            })


class RegionAnalysisView(APIView):
    """
    Returns computed zone scores for a region (Django-computed, no IA).
    Used by frontend to display zones with scores before IA analysis.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, region_name):
        if request.user.role not in IA_ANALYSIS_ROLES | {"AGENT"}:
            return Response({"detail": "Accès refusé."}, status=403)
        campaign = get_active_campaign(request.user)
        if not campaign:
            return Response({"detail": "Aucune campagne active autorisée."}, status=404)
        
        data = compute_region_zones_data(campaign, region_name)
        if request.user.role == "AGENT":
            assigned_names = set(CampagneAffectation.objects.filter(
                campagne=campaign, agent=request.user,
            ).values_list("zone", flat=True))
            data["zones"] = [zone for zone in data["zones"] if zone.get("nom") in assigned_names]
            data["zones_count"] = len(data["zones"])
            data["total_beneficiaries"] = sum(zone.get("beneficiaires", 0) for zone in data["zones"])
        return Response(data)


class RegionAnalysisIAView(APIView):
    """
    Triggers IA analysis for a region's zones.
    Sends Django-computed data to FastAPI/Gemini for human-readable analysis.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, region_name):
        if request.user.role not in IA_ANALYSIS_ROLES:
            return Response({"detail": "Accès refusé."}, status=403)
        campaign = get_active_campaign(request.user)
        if not campaign:
            return Response({"detail": "Aucune campagne active"}, status=404)
        
        # Compute zones data from Django
        zones_data = compute_region_zones_data(campaign, region_name)
        
        # Call IA service for analysis
        try:
            result = call_ia_service(f"/api/ia/regions/{region_name}/analyze", zones_data)
            return Response(result)
        except Exception as e:
            logger.error("Region IA analysis failed (error_type=%s)", type(e).__name__)
            return Response({"detail": "Erreur lors de l'analyse IA"}, status=500)


# ---------------------------------------------------------------------------
# Assistant IA Exécutif — Chat conversationnel (Gérant uniquement)
# ---------------------------------------------------------------------------

def build_chat_context(user):
    """
    Construit le contexte complet de l'organisation depuis PostgreSQL.
    Ce contexte est envoyé à FastAPI/Gemini à chaque question.
    Aucune donnée inventée — tout provient de la base de données.
    """
    now = timezone.now()
    today = now.date()
    org = user.organization

    from django.contrib.auth import get_user_model
    User = get_user_model()

    projects_qs    = Project.objects.filter(organization=org)
    campaigns_qs   = Campaign.objects.filter(organization=org)
    benef_qs       = Beneficiary.objects.filter(organization=org)
    budgets_qs     = Budget.objects.filter(organization=org)
    depenses_qs    = Depense.objects.filter(organization=org)
    agents_qs      = User.objects.filter(organization=org, role="AGENT", is_active=True)

    # --- Projets ---
    projets_actifs = projects_qs.filter(archived=False)
    projets_data = [
        {
            "id": str(p.id),
            "name": p.name,
            "budget": float(p.budgets.aggregate(s=models.Sum("montant"))["s"] or 0),
            "start_date": p.start_date.isoformat() if p.start_date else None,
            "end_date": p.end_date.isoformat() if p.end_date else None,
            "region": p.region or "",
        }
        for p in projets_actifs[:10]
    ]

    # --- Campagnes ---
    active_campaigns = campaigns_qs.filter(statut=Campaign.Statut.EN_COURS)
    campaigns_data = []
    for c in active_campaigns.annotate(nb_ben=models.Count("beneficiaries")):
        campaigns_data.append({
            "id": str(c.id),
            "nom": c.nom,
            "statut": c.statut,
            "date_debut": c.date_debut.isoformat() if c.date_debut else None,
            "date_fin": c.date_fin.isoformat() if c.date_fin else None,
            "jours_restants": (c.date_fin - today).days if c.date_fin else None,
            "beneficiaires_count": c.nb_ben,
        })

    # --- Bénéficiaires ---
    total_benef = benef_qs.count()
    genre_repartition = dict(
        benef_qs.values("sexe").annotate(total=models.Count("id")).values_list("sexe", "total")
    )
    region_repartition = dict(
        benef_qs.values("zone__region")
        .annotate(total=models.Count("id"))
        .values_list("zone__region", "total")
    )
    # Vulnérabilité
    vuln_data = benef_qs.exclude(score_vulnerabilite__isnull=True)
    avg_vuln = vuln_data.aggregate(avg=models.Avg("score_vulnerabilite"))["avg"] or 0
    tres_eleves = vuln_data.filter(score_vulnerabilite__gte=80).count()
    eleves = vuln_data.filter(score_vulnerabilite__gte=60, score_vulnerabilite__lt=80).count()

    # --- Finances ---
    from apps.finance.services import calculate_financial_kpis
    finance_kpis = calculate_financial_kpis(org)
    sum_budgets = finance_kpis["budget_total"]
    sum_depenses = finance_kpis["depenses_totales"]
    sum_financements = finance_kpis["financements_recus"]
    sum_dons = finance_kpis["dons_recus"]
    solde = finance_kpis["solde_tresorerie"]
    taux = finance_kpis["taux_execution"]

    # Dépenses par catégorie
    dep_categories = {
        k: float(v)
        for k, v in depenses_qs.values("categorie")
        .annotate(total=models.Sum("montant"))
        .values_list("categorie", "total")
        if k and v is not None
    }

    # --- Agents ---
    agents_count = agents_qs.count()
    recent_benef = (
        benef_qs.order_by("-created_at")
        .values("prenom", "nom", "created_at")[:5]
    )
    recent_registrations = [
        {
            "nom": f"{b['prenom']} {b['nom']}".strip(),
            "date": b["created_at"].strftime("%d/%m/%Y") if b["created_at"] else None,
        }
        for b in recent_benef
    ]

    return {
        "organisation": str(org) if org else "ONG",
        "date_analyse": today.isoformat(),
        "projets": {
            "total": projets_actifs.count(),
            "liste": projets_data[:10],
            "budget_total_projets": float(sum_budgets),
        },
        "campagnes": {
            "total_actives": active_campaigns.count(),
            "total": campaigns_qs.count(),
            "liste": campaigns_data[:10],
        },
        "beneficiaires": {
            "total": total_benef,
            "repartition_genre": genre_repartition,
            "repartition_region": {k: v for k, v in region_repartition.items() if k},
            "score_vulnerabilite_moyen": round(float(avg_vuln), 1),
            "tres_vulnerables": tres_eleves,
            "vulnerables": eleves,
        },
        "finances": {
            "budget_total": float(sum_budgets),
            "financements_recus": float(sum_financements),
            "dons_recus": float(sum_dons),
            "depenses_totales": float(sum_depenses),
            "solde": solde,
            "taux_execution": taux,
            "depenses_par_categorie": {
                k: float(v) for k, v in dep_categories.items() if k
            },
        },
        "agents": {
            "total_actifs": agents_count,
            "enregistrements_recents": recent_registrations,
        },
        "_security": ai_tenant_identity(user),
    }


def _assistant_intents(question, history):
    """Small deterministic router: data selection stays in Django, never in the LLM."""
    normalized = unicodedata.normalize("NFD", question.lower())
    normalized = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    intent = classify_assistant_intent(question)
    if intent == "OUT_OF_SCOPE":
        return []
    if intent == "ONG_SUMMARY":
        return ["get_ong_summary"]
    if intent == "PROJECT_LIST":
        return ["get_projects"]
    tools = []
    def add(name):
        if name not in tools:
            tools.append(name)

    if any(term in normalized for term in ("bilan", "synthese", "situation de mon ong", "resume global")):
        add("get_ong_summary")
    if any(term in normalized for term in ("activite", "activites", "actualite", "recent", "cette semaine")):
        add("get_recent_activities")
    if any(term in normalized for term in ("retard", "en retard", "depasse")):
        add("get_delayed_projects")
    if any(term in normalized for term in ("probleme", "attention", "alerte", "risque")):
        add("get_delayed_projects")
        add("get_priority_beneficiaries")
    if any(term in normalized for term in ("financ", "budget", "depens", "solde", "don", "financement")):
        add("get_financial_summary")
    if any(term in normalized for term in ("prioritaire", "vulnerable", "vulnerabilite")):
        add("get_priority_beneficiaries")
    if any(term in normalized for term in ("budget", "budgets")):
        add("get_budgets")
    if any(term in normalized for term in ("don", "dons", "donation")):
        add("get_donations")
    if any(term in normalized for term in ("depense", "depenses", "depens")):
        add("get_expenses")
    if any(term in normalized for term in ("zone", "zones")):
        add("get_zones")
    if any(term in normalized for term in ("equipe", "utilisateur", "responsable", "chef")):
        add("get_users")
    if any(term in normalized for term in ("pris en charge", "accompagne")):
        add("get_beneficiary_support")
    if any(term in normalized for term in ("campagne", "campagnes")):
        add("get_active_campaigns")
    if any(term in normalized for term in ("projet", "projets")):
        add("get_projects")
    if any(term in normalized for term in ("rapport", "report")):
        add("prepare_report")
    if any(term in normalized for term in ("cree", "creer", "prepare", "preparer", "nouveau")):
        if "projet" in normalized:
            add("prepare_project_creation")
        if "campagne" in normalized:
            add("prepare_campaign_creation")
    notify_requested = any(term in normalized for term in ("previens", "previen", "previent", "prevenir", "notifie", "informe", "envoie une notification"))
    prior_delay_context = any("retard" in item.get("content", "").lower() for item in history[-6:])
    if notify_requested and ("retard" in normalized or prior_delay_context):
        add("get_delayed_projects")
        add("send_delayed_project_notifications")
    return tools


def _build_agent_tool_results(user, context, tool_names):
    """Execute read-only assistant tools using Django's authenticated tenant scope."""
    from apps.finance.models import Don

    organization_id = user.organization_id
    today = timezone.localdate()
    projects = Project.objects.filter(organization_id=organization_id, archived=False)
    campaigns = Campaign.objects.filter(
        organization_id=organization_id,
        projet__organization_id=organization_id,
    )
    beneficiaries = Beneficiary.objects.filter(organization_id=organization_id)
    results = []
    for name in tool_names:
        if name == "get_ong_summary":
            results.append({
                "tool": name, "title": "Bilan de l’ONG",
                "data": {key: value for key, value in context.items() if key != "_security"},
            })
        elif name == "get_projects":
            rows = list(projects.order_by("end_date").values(
                "id", "name", "region", "start_date", "end_date", "chef_projet__first_name", "chef_projet__last_name"
            )[:50])
            results.append({"tool": name, "title": "Projets de l’ONG", "data": rows})
        elif name == "get_delayed_projects":
            rows = list(projects.filter(end_date__lt=today).order_by("end_date").values(
                "id", "name", "region", "end_date", "chef_projet_id", "chef_projet__first_name", "chef_projet__last_name"
            )[:50])
            results.append({"tool": name, "title": "Projets dont la date de fin est dépassée", "data": rows})
        elif name == "get_active_campaigns":
            rows = list(campaigns.filter(statut=Campaign.Statut.EN_COURS).order_by("date_fin").values(
                "id", "nom", "projet__name", "date_debut", "date_fin", "statut"
            )[:50])
            results.append({"tool": name, "title": "Campagnes en cours", "data": rows})
        elif name == "get_priority_beneficiaries":
            priority = beneficiaries.filter(
                models.Q(statut=Beneficiary.Statut.PRIORITAIRE)
                | models.Q(score_vulnerabilite__gte=80)
            )
            results.append({
                "tool": name,
                "title": "Bénéficiaires prioritaires",
                "data": {"total": priority.distinct().count(), "par_region": list(
                    priority.values("zone__region__nom").annotate(total=models.Count("id", distinct=True)).order_by("-total")[:20]
                )},
            })
        elif name == "get_financial_summary":
            budget_total = Budget.objects.filter(organization_id=organization_id).aggregate(total=models.Sum("montant"))["total"] or 0
            spending = Depense.objects.filter(organization_id=organization_id).aggregate(total=models.Sum("montant"))["total"] or 0
            donations = Don.objects.filter(organization_id=organization_id).aggregate(total=models.Sum("montant"))["total"] or 0
            results.append({"tool": name, "title": "Synthèse financière", "data": {
                "budget_total": float(budget_total), "depenses": float(spending),
                "dons": float(donations), "solde_dons_moins_depenses": float(donations - spending),
                "taux_execution_pct": round(float(spending / budget_total * 100), 2) if budget_total else None,
            }})
        elif name == "get_budgets":
            rows = list(Budget.objects.filter(organization_id=organization_id).order_by("-date").values(
                "id", "projet__name", "montant", "devise", "source_financement", "date", "statut"
            )[:50])
            results.append({"tool": name, "title": "Budgets de l’ONG", "data": rows})
        elif name == "get_donations":
            rows = list(Don.objects.filter(organization_id=organization_id).order_by("-date").values(
                "id", "montant", "devise", "date", "moyen_paiement", "campagne__nom"
            )[:50])
            results.append({"tool": name, "title": "Dons enregistrés", "data": rows})
        elif name == "get_expenses":
            rows = list(Depense.objects.filter(organization_id=organization_id).order_by("-date").values(
                "id", "categorie", "montant", "devise", "date", "statut", "projet__name", "reference"
            )[:50])
            results.append({"tool": name, "title": "Dépenses enregistrées", "data": rows})
        elif name == "get_zones":
            rows = list(Zone.objects.filter(organization_id=organization_id).annotate(
                beneficiaires_total=models.Count("beneficiaries", distinct=True),
                beneficiaires_prioritaires=models.Count("beneficiaries", filter=(
                    models.Q(beneficiaries__statut=Beneficiary.Statut.PRIORITAIRE)
                    | models.Q(beneficiaries__score_vulnerabilite__gte=80)
                ), distinct=True),
            ).values("id", "nom", "region__nom", "departement__nom", "beneficiaires_total", "beneficiaires_prioritaires").order_by("-beneficiaires_prioritaires")[:50])
            results.append({"tool": name, "title": "Zones et bénéficiaires", "data": rows})
        elif name == "get_users":
            from apps.accounts.models import User
            rows = list(User.objects.filter(organization_id=organization_id, is_active=True).order_by("role", "last_name").values(
                "id", "first_name", "last_name", "role"
            )[:50])
            results.append({"tool": name, "title": "Équipe active", "data": rows})
        elif name == "get_beneficiary_support":
            actions = HumanitarianAction.objects.filter(beneficiary__organization_id=organization_id, statut=HumanitarianAction.Statut.REALISEE)
            supported_ids = actions.values("beneficiary_id").distinct()
            results.append({"tool": name, "title": "Bénéficiaires pris en charge", "data": {
                "total": beneficiaries.filter(statut=Beneficiary.Statut.PRIS_EN_CHARGE).count(),
                "actions_realisees": actions.count(),
                "beneficiaires_avec_action": supported_ids.count(),
            }})
        elif name == "get_recent_activities":
            activity_rows = []
            for item in projects.order_by("-updated_at")[:10]:
                activity_rows.append({"type": "projet", "nom": item.name, "date": item.updated_at.isoformat()})
            for item in campaigns.order_by("-created_at")[:10]:
                activity_rows.append({"type": "campagne", "nom": item.nom, "date": item.created_at.isoformat()})
            for item in beneficiaries.order_by("-created_at")[:10]:
                activity_rows.append({"type": "bénéficiaire", "date": item.created_at.isoformat()})
            for item in Depense.objects.filter(organization_id=organization_id).order_by("-created_at")[:10]:
                activity_rows.append({"type": "dépense", "nom": item.categorie, "date": item.created_at.isoformat()})
            activity_rows.sort(key=lambda item: item["date"], reverse=True)
            results.append({"tool": name, "title": "Activités récentes", "data": activity_rows[:20]})
        elif name == "prepare_report":
            results.append({"tool": name, "title": "Rapport préparé", "data": {
                "status": "draft_ready", "created_at": timezone.now().isoformat(),
                "message": "Le résumé est prêt dans cette conversation. Aucune diffusion externe n’a été effectuée.",
            }})
        elif name == "prepare_project_creation":
            results.append({"tool": name, "title": "Préparation d’un projet", "action": {
                "risk": "HIGH", "requires_user_submission": True,
                "route": "/gerant/projets/creer",
                "message": "Le formulaire de projet va s’ouvrir. Vérifiez les informations, les responsables, le budget et les critères, puis soumettez-le vous-même. Rien n’a été créé par l’assistant.",
                "required_fields": ["nom", "région", "objectif", "dates", "chef de projet", "responsable finance", "critères totalisant 100 points"],
            }})
        elif name == "prepare_campaign_creation":
            results.append({"tool": name, "title": "Préparation d’une campagne", "action": {
                "risk": "MEDIUM", "requires_user_submission": True,
                "message": "La création d’une campagne se fait par le Chef de projet. L’assistant ne peut pas la créer avec le rôle Gérant.",
                "required_fields": ["projet", "type", "zones", "dates"],
            }})
        elif name == "send_delayed_project_notifications":
            from apps.accounts.models import User
            delayed = next((result.get("data", []) for result in results if result.get("tool") == "get_delayed_projects"), [])
            eligible = []
            for project in delayed:
                manager = User.objects.filter(
                    pk=project.get("chef_projet_id"),
                    organization_id=organization_id,
                    role=User.Role.CHEF_PROJET,
                    is_active=True,
                ).first() if project.get("chef_projet_id") else None
                if manager:
                    eligible.append((project, manager))

            normalized_question = unicodedata.normalize("NFD", question.lower())
            normalized_question = "".join(char for char in normalized_question if unicodedata.category(char) != "Mn")
            named_matches = [
                pair for pair in eligible
                if unicodedata.normalize("NFD", pair[0]["name"].lower())
                .encode("ascii", "ignore").decode("ascii") in normalized_question
            ]
            send_all = any(term in normalized_question for term in ("tous les chefs", "chefs concernes", "chaque chef", "tous les responsables"))
            if len(named_matches) == 1:
                eligible = named_matches
            elif len(eligible) > 1 and not send_all:
                results.append({
                    "tool": name,
                    "title": "Choisissez le projet à notifier",
                    "data": {
                        "sent": 0,
                        "message": "Plusieurs projets ont une date de fin dépassée. Je n’ai envoyé aucune notification; précisez le projet ou demandez de notifier tous les chefs concernés.",
                        "candidates": [{"id": project["id"], "name": project["name"]} for project, _manager in eligible],
                    },
                })
                continue
            delivered = []
            for project, manager in eligible:
                title = "Suivi de projet requis"
                message = (
                    f"Le projet « {project['name']} » a dépassé sa date de fin prévue "
                    f"({project['end_date']}). Merci de mettre à jour son état d’avancement."
                )
                if InAppNotification.objects.filter(
                    recipient=manager,
                    project_id=project["id"],
                    title=title,
                    created_at__gte=timezone.now() - timezone.timedelta(minutes=5),
                ).exists():
                    continue
                notification = InAppNotification.objects.create(
                    recipient=manager,
                    organization_id=organization_id,
                    created_by=user,
                    project_id=project["id"],
                    title=title,
                    message=message,
                    source="AI_ASSISTANT",
                )
                delivered.append({
                    "notification_id": str(notification.id),
                    "project": project["name"],
                    "recipient": manager.full_name,
                })
            results.append({
                "tool": name,
                "title": "Notifications internes envoyées",
                "data": {"sent": len(delivered), "notifications": delivered},
            })
    return results


def _agent_fallback_answer(question, context, tool_results):
    """Return a short factual response from Django tool results when Gemini is down."""
    org_name = context.get("organisation", "votre organisation")
    by_tool = {result.get("tool"): result for result in tool_results}
    if "send_delayed_project_notifications" in by_tool:
        data = by_tool["send_delayed_project_notifications"].get("data", {})
        if data.get("message"):
            return data["message"]
        return f"{data.get('sent', 0)} notification(s) interne(s) envoyée(s) aux chefs de projet concernés."
    if any(result.get("action") for result in tool_results):
        return "L’action est préparée, mais elle n’a pas été exécutée. Consultez la proposition et le formulaire : Django vérifiera les droits et les données lors de la soumission."
    if "get_financial_summary" in by_tool:
        data = by_tool["get_financial_summary"].get("data", {})
        return (
            f"Synthèse financière de {org_name} :\n"
            f"- Budget : {data.get('budget_total', 0):,.0f} FCFA\n"
            f"- Dépenses : {data.get('depenses', 0):,.0f} FCFA\n"
            f"- Dons : {data.get('dons', 0):,.0f} FCFA\n"
            f"- Solde dons moins dépenses : {data.get('solde_dons_moins_depenses', 0):,.0f} FCFA"
        )
    if "get_delayed_projects" in by_tool:
        rows = by_tool["get_delayed_projects"].get("data", [])
        if not rows:
            return "Aucun projet dont la date de fin est dépassée n’a été trouvé. Les données ne permettent pas de conclure sur l’avancement réel des projets."
        lines = [f"{row['name']} — date de fin : {row['end_date']}" for row in rows[:10]]
        return "La date de fin est dépassée pour :\n- " + "\n- ".join(lines) + "\n\nCela ne suffit pas à confirmer un retard d’avancement."
    if "get_priority_beneficiaries" in by_tool:
        data = by_tool["get_priority_beneficiaries"].get("data", {})
        return f"{data.get('total', 0)} bénéficiaire(s) prioritaire(s) ont été recensés dans {org_name}."
    if "get_active_campaigns" in by_tool:
        rows = by_tool["get_active_campaigns"].get("data", [])
        return "Aucune campagne en cours n’a été trouvée." if not rows else (
            "Campagnes en cours :\n- " + "\n- ".join(
                f"{row['nom']} (projet : {row.get('projet__name') or 'non précisé'})" for row in rows[:10]
            )
        )
    if "get_projects" in by_tool:
        rows = by_tool["get_projects"].get("data", [])
        return "Aucun projet n’a été trouvé." if not rows else (
            f"{len(rows)} projet(s) affiché(s) :\n- " + "\n- ".join(
                f"{row['name']} — {row.get('region') or 'région non précisée'}" for row in rows[:10]
            )
        )
    if "get_recent_activities" in by_tool:
        rows = by_tool["get_recent_activities"].get("data", [])
        return "Aucune activité récente n’a été trouvée." if not rows else (
            "Activités récentes :\n- " + "\n- ".join(
                f"{row.get('type', 'activité')} — {row.get('nom') or 'élément enregistré'} ({row.get('date', '')[:10]})"
                for row in rows[:10]
            )
        )
    for tool_name, label, name_key in (
        ("get_budgets", "Budgets", "projet__name"),
        ("get_donations", "Dons", "campagne__nom"),
        ("get_expenses", "Dépenses", "categorie"),
        ("get_zones", "Zones", "nom"),
        ("get_users", "Membres de l’équipe", "first_name"),
    ):
        if tool_name in by_tool:
            rows = by_tool[tool_name].get("data", [])
            if not rows:
                return f"Aucun élément {label.lower()} n’a été trouvé."
            if tool_name == "get_users":
                return f"{len(rows)} membre(s) actif(s) dans l’équipe :\n- " + "\n- ".join(
                    f"{row.get('first_name', '')} {row.get('last_name', '')} — {row.get('role', '')}".strip(" —") for row in rows[:10]
                )
            return f"{label} ({len(rows)} résultat(s)) :\n- " + "\n- ".join(
                f"{row.get(name_key) or row.get('nom') or 'Élément'} — {row.get('montant', row.get('beneficiaires_total', ''))} {row.get('devise', '')} {row.get('statut', '')}".strip()
                for row in rows[:10]
            )
    if "get_beneficiary_support" in by_tool:
        data = by_tool["get_beneficiary_support"].get("data", {})
        return (
            f"{data.get('total', 0)} bénéficiaire(s) ont le statut pris en charge. "
            f"{data.get('beneficiaires_avec_action', 0)} bénéficiaire(s) ont au moins une aide réalisée."
        )
    if "prepare_report" in by_tool:
        return by_tool["prepare_report"].get("data", {}).get("message", "Le résumé du rapport est prêt dans cette conversation.")
    projects = context.get("projets", {})
    campaigns = context.get("campagnes", {})
    beneficiaries = context.get("beneficiaires", {})
    return (
        f"Bilan de {org_name} : {projects.get('total', 0)} projet(s) actif(s), "
        f"{campaigns.get('total_actives', 0)} campagne(s) en cours et "
        f"{beneficiaries.get('total', 0)} bénéficiaire(s) recensé(s)."
    )

class AssistantChatView(APIView):
    """
    POST /api/assistant/chat
    Endpoint conversationnel de l'Assistant IA Exécutif — Gérant uniquement.
    """
    permission_classes = [IsAuthenticated, IsAccountActive]

    IA_CHAT_URL = "http://ia_service:8001/api/ia/chat"

    def get(self, request):
        if request.user.role not in ("GERANT", "SUPER_ADMIN"):
            return Response({"detail": "Accès réservé au Gérant."}, status=403)
        try:
            conversation_id = uuid.UUID(str(request.query_params.get("session_id")))
        except (TypeError, ValueError, AttributeError):
            return Response({"messages": []})
        rows = AssistantInteraction.objects.filter(
            conversation_id=conversation_id,
            user=request.user,
            organization_id=request.user.organization_id,
        ).order_by("-created_at")[:12]
        messages = []
        for row in reversed(list(rows)):
            messages.extend([
                {"role": "user", "content": safe_audit_text(row.request_text, limit=4000)},
                {"role": "assistant", "content": safe_audit_text(row.response_text, limit=12000)},
            ])
        return Response({"messages": messages[-24:]})

    def post(self, request):
        if request.user.role not in ("GERANT", "SUPER_ADMIN"):
            return Response(
                {"detail": "Accès réservé au Gérant."},
                status=403,
            )

        question = (request.data.get("question") or "").strip()
        if not question:
            return Response({"detail": "La question ne peut pas être vide."}, status=400)
        if len(question) > 4000:
            return Response({"detail": "La demande ne peut pas dépasser 4 000 caractères."}, status=400)
        try:
            conversation_id = uuid.UUID(str(request.data.get("session_id") or uuid.uuid4()))
        except (TypeError, ValueError, AttributeError):
            return Response({"detail": "Identifiant de conversation invalide."}, status=400)
        # Rebuild context from server rows owned by this user and organization.
        prior_rows = list(
            AssistantInteraction.objects.filter(
                conversation_id=conversation_id,
                user=request.user,
                organization_id=request.user.organization_id,
            ).order_by("-created_at")[:6]
        )
        history = []
        for interaction in reversed(prior_rows):
            history.extend([
                {"role": "user", "content": safe_audit_text(interaction.request_text)},
                {"role": "assistant", "content": safe_audit_text(interaction.response_text)},
            ])
        history = history[-12:]
        safe_question = safe_audit_text(question, limit=4000)
        blocked_message = input_guardrail_message(
            safe_question + "\n" + "\n".join(item["content"] for item in history)
        )
        if blocked_message:
            return Response({
                "answer": blocked_message,
                "generated_at": timezone.now().isoformat(),
                "session_id": str(conversation_id),
                "tool_results": [],
                "tools_used": [],
            })
        project_answer = handle_project_creation(
            request.user, conversation_id, question, request,
        )
        if project_answer is not None:
            return Response({
                "answer": project_answer,
                "generated_at": timezone.now().isoformat(),
                "session_id": str(conversation_id),
                "tool_results": [],
                "tools_used": ["project_creation_conversation"],
            })
        out_of_scope = out_of_scope_message(safe_question)
        if out_of_scope:
            return Response({
                "answer": out_of_scope,
                "generated_at": timezone.now().isoformat(),
                "session_id": str(conversation_id),
                "tool_results": [],
                "tools_used": [],
            })

        # Collect real data from PostgreSQL
        try:
            context = build_chat_context(request.user)
            tool_names = _assistant_intents(question, history)
            tool_results = _build_agent_tool_results(request.user, context, tool_names)
            context["agent_tools"] = tool_results
        except Exception as e:
            logger.error("build_chat_context failed (error_type=%s)", type(e).__name__)
            return Response(
                {"detail": "Erreur lors de la collecte des données."},
                status=500,
            )

        # Sérialiser le payload en gérant Decimal, date, UUID
        import decimal
        import datetime as dt
        import uuid as uuid_mod

        class _SafeEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, decimal.Decimal):
                    return float(obj)
                if isinstance(obj, (dt.date, dt.datetime)):
                    return obj.isoformat()
                if isinstance(obj, uuid_mod.UUID):
                    return str(obj)
                return super().default(obj)

        # Forward to FastAPI/Gemini
        payload = {
            "tenant": ai_tenant_identity(request.user),
            "question": safe_question,
            "context": context,
            "history": history,
        }
        payload_bytes = json.dumps(payload, cls=_SafeEncoder).encode("utf-8")

        try:
            response = post_to_ai_service(
                self.IA_CHAT_URL,
                body=payload_bytes,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            result["answer"] = safe_audit_text(result.get("answer", ""), limit=12000)
            result.update({
                "session_id": str(conversation_id),
                "tool_results": tool_results,
                "tools_used": tool_names,
            })
            AssistantInteraction.objects.create(
                conversation_id=conversation_id,
                user=request.user,
                organization_id=request.user.organization_id,
                request_text=safe_question,
                response_text=safe_audit_text(result.get("answer", "")),
                tools_used=tool_names,
            )
            return Response(result)
        except ImproperlyConfigured:
            return Response(
                {"detail": "Le service IA n'est pas configuré."},
                status=500,
            )
        except requests.Timeout:
            AssistantInteraction.objects.create(
                conversation_id=conversation_id,
                user=request.user,
                organization_id=request.user.organization_id,
                request_text=safe_question,
                response_text="Le service IA a dépassé le délai. Les résultats Django restent disponibles.",
                tools_used=tool_names,
            )
            return Response(
                {
                    "answer": _agent_fallback_answer(question, context, tool_results),
                    "generated_at": timezone.now().isoformat(),
                    "session_id": str(conversation_id),
                    "tool_results": tool_results,
                    "tools_used": tool_names,
                },
            )
        except requests.RequestException as e:
            logger.error("AssistantChatView IA call failed (%s)", type(e).__name__)

            # Les outils Django restent utilisables si le modèle IA est indisponible.
            ans = _agent_fallback_answer(question, context, tool_results)

            AssistantInteraction.objects.create(
                conversation_id=conversation_id,
                user=request.user,
                organization_id=request.user.organization_id,
                request_text=safe_question,
                response_text=safe_audit_text(ans),
                tools_used=tool_names,
            )

            return Response(
                {
                    "answer": ans,
                    "generated_at": timezone.now().isoformat(),
                    "session_id": str(conversation_id),
                    "tool_results": tool_results,
                    "tools_used": tool_names,
                },
            )


class AssistantAudioTranscriptionView(APIView):
    """Receive a Gerant voice note and proxy it to the private IA service."""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    MAX_AUDIO_BYTES = 15 * 1024 * 1024
    MAX_DURATION_SECONDS = 120
    ALLOWED_TYPES = {
        "audio/webm", "audio/ogg", "audio/wav", "audio/x-wav",
        "audio/mpeg", "audio/mp3", "audio/mp4", "audio/x-m4a",
    }

    def post(self, request):
        if request.user.role not in {"GERANT", "FINANCE"} or not request.user.organization_id:
            return Response({"detail": "Accès réservé aux responsables autorisés de l’organisation."}, status=403)

        audio_file = request.FILES.get("audio")
        if not audio_file:
            return Response({"detail": "Sélectionnez un message vocal."}, status=400)
        if audio_file.size > self.MAX_AUDIO_BYTES:
            return Response({"detail": "Le fichier audio est trop volumineux. Enregistrez un message plus court."}, status=413)

        media_type = (audio_file.content_type or "").split(";", 1)[0].strip().lower()
        if media_type not in self.ALLOWED_TYPES:
            return Response({"detail": "Format audio non pris en charge."}, status=415)
        try:
            duration = int(request.data.get("duration_seconds", 0))
        except (TypeError, ValueError):
            return Response({"detail": "Durée audio invalide."}, status=400)
        if duration < 1 or duration > self.MAX_DURATION_SECONDS:
            return Response({"detail": "La durée maximale d’un message vocal est de 2 minutes."}, status=400)

        filename = audio_file.name.replace("\\", "/").split("/")[-1][:100] or "message-vocal.webm"
        url = f"{settings.IA_SERVICE_URL.rstrip('/')}/api/ia/audio/transcribe"
        try:
            response = post_to_ai_service(
                url,
                body=audio_file.read(),
                headers={
                    "Content-Type": media_type,
                    "X-Audio-Filename": filename,
                    "X-Audio-Duration-Seconds": str(duration),
                },
                timeout=90,
            )
        except ImproperlyConfigured:
            return Response({"detail": "Le service IA n’est pas configuré."}, status=503)
        except requests.Timeout:
            return Response({"detail": "La transcription a dépassé le délai. Réessayez avec un message plus court."}, status=503)
        except requests.RequestException:
            logger.warning("Assistant audio transcription service unavailable")
            return Response({"detail": "La transcription vocale est temporairement indisponible."}, status=503)

        if not response.ok:
            try:
                detail = response.json().get("detail")
            except (ValueError, AttributeError):
                detail = None
            status_code = response.status_code if response.status_code in (400, 413, 415, 422) else 503
            return Response({"detail": detail or "La transcription vocale a échoué. Réessayez."}, status=status_code)

        try:
            transcription = response.json().get("transcription", "").strip()
        except (ValueError, AttributeError):
            transcription = ""
        if not transcription:
            return Response({"detail": "Je n’ai pas réussi à comprendre clairement votre message vocal. Pouvez-vous réessayer ?"}, status=422)
        return Response({"transcription": transcription})
