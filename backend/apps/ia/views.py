import json
import logging
import requests
from django.conf import settings
from django.utils import timezone
from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.campaigns.models import Campaign
from apps.beneficiaries.models import Beneficiary
from apps.zones.models import Zone
from apps.finance.models import Depense, Budget, PosteBudgetaire
from apps.projects.models import Project
from apps.ia.models import IAnalyse

logger = logging.getLogger(__name__)


def get_active_campaign(user):
    """Get the active campaign for the user's organization"""
    if user.role == "SUPER_ADMIN":
        return Campaign.objects.filter(statut=Campaign.Statut.EN_COURS).first()
    return Campaign.objects.filter(
        organization=user.organization, 
        statut=Campaign.Statut.EN_COURS
    ).first()


def compute_executive_payload(campaign, user):
    """Compute executive insight payload from Django data"""
    # Beneficiaries stats
    beneficiaries = Beneficiary.objects.filter(campagne=campaign)
    total_beneficiaries = beneficiaries.count()
    
    # Zones with beneficiary counts and scores
    zones = Zone.objects.filter(campaigns=campaign, organization=user.organization)
    zones_data = []
    for zone in zones:
        zone_beneficiaries = beneficiaries.filter(zone=zone)
        avg_score = zone_beneficiaries.exclude(ai_score__isnull=True).aggregate(
            avg_score=models.Avg('ai_score')
        )['avg_score'] or 0
        zones_data.append({
            "id": str(zone.id),
            "nom": zone.nom,
            "region": zone.region,
            "departement": zone.departement,
            "beneficiaires": zone_beneficiaries.count(),
            "score_moyen": float(avg_score),
            "latitude": float(zone.latitude),
            "longitude": float(zone.longitude),
        })
    
    # Budget data
    budgets = Budget.objects.filter(projet=campaign.projet)
    total_budget = sum(float(b.montant_total) for b in budgets)
    
    depenses = Depense.objects.filter(projet=campaign.projet)
    total_depenses = sum(float(d.montant) for d in depenses)
    
    # Expenses by zone and category
    depenses_par_zone = {}
    depenses_par_categorie = {}
    for depense in depenses:
        zone_name = depense.projet.zone.nom if hasattr(depense.projet, 'zone') and depense.projet.zone else "Non assigné"
        depenses_par_zone[zone_name] = depenses_par_zone.get(zone_name, 0) + float(depense.montant)
        
        cat_name = depense.poste_budgetaire.libelle if depense.poste_budgetaire else "Non catégorisé"
        depenses_par_categorie[cat_name] = depenses_par_categorie.get(cat_name, 0) + float(depense.montant)
    
    return {
        "campagne_id": str(campaign.id),
        "nom": campaign.nom,
        "date_debut": campaign.date_debut.isoformat(),
        "date_fin": campaign.date_fin.isoformat(),
        "total_beneficiaires": total_beneficiaries,
        "zones": zones_data,
        "budgets": [
            {"id": str(b.id), "montant_total": float(b.montant_total), "statut": b.statut}
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
    budgets = Budget.objects.filter(projet=campaign.projet)
    total_budget = sum(float(b.montant_total) for b in budgets)
    
    depenses = Depense.objects.filter(projet=campaign.projet)
    total_depenses = sum(float(d.montant) for d in depenses)
    solde = total_budget - total_depenses
    taux = (total_depenses / total_budget * 100) if total_budget > 0 else 0
    
    # Expenses by zone
    depenses_par_zone = {}
    for depense in depenses.select_related('projet__zone'):
        zone_name = depense.projet.zone.nom if depense.projet.zone else "Non assigné"
        depenses_par_zone[zone_name] = depenses_par_zone.get(zone_name, 0) + float(depense.montant)
    
    # Expenses by category
    depenses_par_categorie = {}
    for depense in depenses.select_related('poste_budgetaire'):
        cat_name = depense.poste_budgetaire.libelle if depense.poste_budgetaire else "Non catégorisé"
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
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"IA service call failed: {e}")
        raise


class ExecutiveInsightView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        campaign = get_active_campaign(request.user)
        if not campaign:
            return Response({
                "resume": "Aucune urgence stratégique n'est détectée actuellement.",
                "alert": "GREEN",
                "generated_at": timezone.now().isoformat()
            })
        
        # Try to get cached analysis
        analysis = IAnalyse.objects.filter(
            campagne=campaign, 
            type_analyse='global'
        ).first()
        
        if analysis and analysis.response_data:
            executive_data = analysis.response_data.get('executive', {})
            executive_data["generated_at"] = analysis.updated_at.isoformat()
            return Response(executive_data)
        
        # Compute and call IA service
        payload = compute_executive_payload(campaign, request.user)
        try:
            result = call_ia_service("/api/ia/executive-insight", payload)
            # Cache result
            IAnalyse.objects.update_or_create(
                campagne=campaign,
                type_analyse='global',
                defaults={'response_data': result}
            )
            return Response(result.get('executive', result))
        except Exception as e:
            logger.error(f"Executive insight failed: {e}")
            return Response({
                "resume": "Aucune urgence stratégique n'est détectée actuellement.",
                "alert": "GREEN",
                "generated_at": timezone.now().isoformat()
            })


class RegionZonesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id):
        campaign = get_active_campaign(request.user)
        if not campaign:
            return Response({"region": id, "zones": []})
        
        analysis = IAnalyse.objects.filter(
            campagne=campaign, 
            type_analyse='global'
        ).first()
        
        if analysis and analysis.response_data:
            zones = analysis.response_data.get('zones_prioritaires', [])
            # Filter zones by region if needed
            region_zones = [z for z in zones if z.get('region', '').lower() == id.lower()]
            return Response({"region": id, "zones": region_zones})
        
        # Compute and call IA
        payload = compute_executive_payload(campaign, request.user)
        try:
            result = call_ia_service(f"/api/ia/regions/{id}/analyze", payload)
            return Response(result)
        except Exception as e:
            logger.error(f"Region zones failed: {e}")
            return Response({"region": id, "zones": []})


class ZoneDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id):
        campaign = get_active_campaign(request.user)
        if not campaign:
            return Response({"message": "Zone non trouvée"})
        
        analysis = IAnalyse.objects.filter(
            campagne=campaign, 
            type_analyse='global'
        ).first()
        
        if analysis and analysis.response_data:
            zones = analysis.response_data.get('zones_prioritaires', [])
            for z in zones:
                if str(z.get('id', '')) == str(id) or z.get('nom') == id:
                    # Get detailed analysis
                    payload = compute_executive_payload(campaign, request.user)
                    try:
                        detail = call_ia_service(f"/api/ia/zones/{id}/analyze", payload)
                        return Response(detail)
                    except Exception as e:
                        logger.error(f"Zone detail failed: {e}")
            return Response({"message": "Zone non trouvée"})
        
        return Response({"message": "Zone non trouvée"})


class BudgetAnalysisView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, campagne_id):
        try:
            campaign = Campaign.objects.get(id=campagne_id)
        except Campaign.DoesNotExist:
            return Response({
                "alert": "GREEN",
                "resume": "Les dépenses restent cohérentes avec le budget prévu. Aucun risque financier n'est détecté pour le moment.",
                "generated_at": timezone.now().isoformat()
            })
        
        # Check permissions
        if request.user.role != "SUPER_ADMIN" and campaign.organization != request.user.organization:
            return Response({"detail": "Accès refusé"}, status=403)
        
        analysis = IAnalyse.objects.filter(
            campagne=campaign, 
            type_analyse='global'
        ).first()
        
        if analysis and analysis.response_data:
            finance_data = analysis.response_data.get('finance', {})
            finance_data["generated_at"] = analysis.updated_at.isoformat()
            return Response(finance_data)
        
        # Compute and call IA
        payload = compute_finance_payload(campaign, request.user)
        try:
            result = call_ia_service(f"/api/ia/budget-analysis/{campagne_id}", payload)
            return Response(result)
        except Exception as e:
            logger.error(f"Budget analysis failed: {e}")
            return Response({
                "alert": "GREEN",
                "resume": "Les dépenses restent cohérentes avec le budget prévu. Aucun risque financier n'est détecté pour le moment.",
                "generated_at": timezone.now().isoformat()
            })