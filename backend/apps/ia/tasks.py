import logging
import requests
from django.conf import settings
from celery import shared_task
from django.utils import timezone
from django.db import models

from apps.campaigns.models import Campaign
from apps.beneficiaries.models import Beneficiary
from apps.zones.models import Zone
from apps.finance.models import Depense, Budget
from apps.ia.models import IAnalyse
from apps.common.interservice import post_to_ai_service
from apps.accounts.models import User

logger = logging.getLogger(__name__)


def _tenant_consistent_expenses_q(organization_id):
    return (
        (models.Q(projet__isnull=True) | models.Q(projet__organization_id=organization_id))
        & (models.Q(budget__isnull=True) | models.Q(
            budget__organization_id=organization_id,
            budget__projet__organization_id=organization_id,
        ))
        & (models.Q(ligne_budgetaire__isnull=True) | models.Q(
            ligne_budgetaire__budget__organization_id=organization_id,
            ligne_budgetaire__budget__projet__organization_id=organization_id,
        ))
        & (models.Q(campagne__isnull=True) | models.Q(
            campagne__organization_id=organization_id,
            campagne__projet__organization_id=organization_id,
        ))
    )


def compute_executive_payload(campaign):
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
    zones = Zone.objects.filter(campaigns=campaign, organization=campaign.organization)
    zones_data = []
    for zone in zones:
        zone_beneficiaries = beneficiaries.filter(zone=zone)
        avg_score = zone_beneficiaries.exclude(score_vulnerabilite__isnull=True).aggregate(
            avg_score=models.Avg('score_vulnerabilite')
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
    budgets = Budget.objects.filter(
        projet=campaign.projet, organization_id=campaign.organization_id,
    )
    total_budget = sum(float(b.montant) for b in budgets)
    
    depenses = Depense.objects.filter(
        models.Q(projet=campaign.projet)
        | models.Q(budget__projet=campaign.projet)
        | models.Q(ligne_budgetaire__budget__projet=campaign.projet)
        | models.Q(campagne=campaign),
        _tenant_consistent_expenses_q(campaign.organization_id),
        organization_id=campaign.organization_id,
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


def compute_finance_payload(campaign):
    """Compute finance payload for budget analysis"""
    budgets = Budget.objects.filter(
        projet=campaign.projet, organization_id=campaign.organization_id,
    )
    total_budget = sum(float(b.montant) for b in budgets)
    
    depenses = Depense.objects.filter(
        models.Q(projet=campaign.projet)
        | models.Q(budget__projet=campaign.projet)
        | models.Q(ligne_budgetaire__budget__projet=campaign.projet)
        | models.Q(campagne=campaign),
        _tenant_consistent_expenses_q(campaign.organization_id),
        organization_id=campaign.organization_id,
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


@shared_task
def run_ia_analyses():
    """Cron job: runs every 6 hours for each ACTIVE campaign"""
    active_campaigns = Campaign.objects.filter(statut=Campaign.Statut.EN_COURS)
    updated = 0
    
    for campaign in active_campaigns:
        try:
            if not campaign.organization_id or campaign.projet.organization_id != campaign.organization_id:
                logger.error(
                    "Skipping IA analysis for campaign %s: campaign/project organization mismatch",
                    campaign.pk,
                )
                continue
            # Compute payloads
            executive_payload = compute_executive_payload(campaign)
            finance_payload = compute_finance_payload(campaign)
            
            # Call IA service for all analyses
            combined_payload = {
                **executive_payload,
                **finance_payload,
            }
            
            response = post_to_ai_service(
                f"{settings.IA_SERVICE_URL}/api/ia/analyze-all",
                payload=combined_payload,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                IAnalyse.objects.update_or_create(
                    campagne=campaign,
                    type_analyse='global',
                    defaults={'response_data': data}
                )
                updated += 1
                logger.info(f"IA analysis completed for campaign {campaign.id}")
            else:
                logger.error("IA service failed for campaign %s (status=%s)", campaign.id, response.status_code)
                
        except Exception as e:
            logger.error("Error calling IA service for campaign %s (error_type=%s)", campaign.id, type(e).__name__)
            
    logger.info(f"IA analyses complete. updated={updated}")
    return updated

@shared_task
def index_data_for_rag():
    """Extracts data from Django and sends it to FastAPI /api/ia/index to fill ChromaDB."""
    by_organization = {}

    def add_document(organization_id, document, metadata, document_id):
        if not isinstance(organization_id, int) or organization_id <= 0:
            raise ValueError("RAG documents require a valid organization tenant.")
        batch = by_organization.setdefault(organization_id, {"documents": [], "metadatas": [], "ids": []})
        batch["documents"].append(document)
        batch["metadatas"].append({**metadata, "organization_id": organization_id, "document_id": document_id})
        batch["ids"].append(document_id)

    # 1. Index Campaigns
    # This scheduled job builds separate tenant batches. Validate each tenant
    # lineage explicitly so inconsistent rows are rejected and observable.
    campaigns = Campaign.objects.select_related("projet").all()
    for camp in campaigns:
        org_id = camp.organization_id
        if not org_id or camp.projet.organization_id != org_id:
            logger.error(
                "Skipping RAG campaign %s: campaign/project organization mismatch",
                camp.pk,
            )
            continue
        org_id = int(org_id)
        budgets = Budget.objects.filter(
            projet=camp.projet,
            organization_id=org_id,
            projet__organization_id=org_id,
        )
        total_budget = sum(float(b.montant) for b in budgets)
        depenses = Depense.objects.filter(
            projet=camp.projet,
            organization_id=org_id,
            projet__organization_id=org_id,
        )
        total_depenses = sum(float(d.montant) for d in depenses)

        doc_text = f"Campagne: {camp.nom}\nDescription: {camp.description}\n"
        doc_text += f"Date début: {camp.date_debut} Date fin: {camp.date_fin}\n"
        doc_text += f"Budget total: {total_budget} FCFA. Dépenses totales: {total_depenses} FCFA.\n"

        add_document(org_id, doc_text, {"type": "campaign", "id": str(camp.id), "nom": camp.nom, "source": "campaign"}, f"campaign_{camp.id}")

    # 2. Index Zones
    zones = Zone.objects.all()
    for zone in zones:
        org_id = zone.organization_id
        if not org_id:
            logger.error("Skipping RAG zone %s: organization is missing", zone.pk)
            continue
        org_id = int(org_id)
        beneficiaires_count = Beneficiary.objects.filter(
            zone=zone,
            organization_id=org_id,
            campagne__organization_id=org_id,
            campagne__projet__organization_id=org_id,
            campagne__zones=zone,
        ).distinct().count()
        doc_text = f"Zone d'intervention: {zone.nom}\nRégion: {zone.region}\nDépartement: {zone.departement}\n"
        doc_text += f"Nombre de bénéficiaires: {beneficiaires_count}\n"
        add_document(org_id, doc_text, {"type": "zone", "id": str(zone.id), "region": str(zone.region), "source": "zone"}, f"zone_{zone.id}")

    if not by_organization:
        return "No data to index"

    results = {}
    for organization_id, batch in by_organization.items():
        # The tenant claim is derived from a real, active organization manager.
        manager = User.objects.filter(
            organization_id=organization_id, role=User.Role.GERANT,
            status=User.Status.ACTIVE, is_active=True,
        ).order_by("id").first()
        if manager is None:
            logger.error("Skipping RAG indexing for organization %s: no active manager", organization_id)
            results[str(organization_id)] = "No active organization manager"
            continue
        payload = {
            **batch,
            "tenant": {
                "organization_id": organization_id,
                "user_id": manager.pk,
                "role": manager.role,
            },
        }
        try:
            response = post_to_ai_service(
                f"{settings.IA_SERVICE_URL}/api/ia/index",
                payload=payload, timeout=60,
            )
            response.raise_for_status()
            results[str(organization_id)] = response.json()
        except Exception as e:
            logger.error("Failed to index RAG data for organization %s: %s", organization_id, e)
            results[str(organization_id)] = str(e)
    return results
