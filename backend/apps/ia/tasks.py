import json
import logging
import urllib.request
import urllib.error

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from apps.campaigns.models import Campaign
from apps.beneficiaries.services import build_zone_ranking
from apps.finance.services import analyse_budgetaire

logger = logging.getLogger(__name__)


def _post(path, payload):
    url = f"{settings.IA_SERVICE_URL}{path}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        logger.error("IA service error %s for %s: %s", exc.code, url, exc.reason)
        raise
    except Exception as exc:
        logger.error("IA service call failed for %s: %s", url, exc)
        raise


@shared_task
def run_ia_analyses():
    campaigns = Campaign.objects.filter(organization__isnull=False).distinct("organization")
    for campaign in campaigns:
        if campaign.statut.upper() != "ACTIVE":
            continue

        try:
            projet = campaign.projet
            zone_ranking = build_zone_ranking(campaign)

            priorisation_payload = {
                "campagne": {
                    "id": str(campaign.id),
                    "nom": campaign.nom,
                    "statut": campaign.statut,
                },
                "projet": {
                    "id": projet.id,
                    "nom": projet.name,
                },
                "zones": zone_ranking,
            }
            _post("/api/ia/priorisation", priorisation_payload)

            budget_data = analyse_budgetaire(projet)
            budget_payload = {
                "projet": projet.name,
                "budget_total": budget_data["budget_total"],
                "dons_recus": budget_data["budget_total"],
                "depenses_totales": budget_data["depenses_totales"],
                "solde": budget_data["solde"],
                "taux_execution": budget_data["taux_execution"],
                "depenses": [],
            }
            _post("/api/ia/budget", budget_payload)
        except Exception as exc:
            logger.exception("Erreur IA pour la campagne %s : %s", campaign.id, exc)
