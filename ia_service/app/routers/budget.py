import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.schemas.budget import BudgetRequest, BudgetResponse
from app.services.gemini_service import call_gemini
from app.services.response_parser import parse_json_response

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/api/ia/budget", response_model=BudgetResponse)
async def analyser_budget(request: BudgetRequest):
    try:
        raw = call_gemini(request.model_dump())
        data = parse_json_response(raw)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Erreur lors de l'appel à Gemini pour le budget.")
        raise HTTPException(status_code=500, detail="Erreur du service IA.") from exc

    try:
        return BudgetResponse(
            generated_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            resume=data.get("resume", ""),
            alerte=data.get("alerte", ""),
            zone_plus_depensiere=data.get("zone_plus_depensiere", ""),
            categorie_plus_depensiere=data.get("categorie_plus_depensiere", ""),
            recommandation=data.get("recommandation", ""),
        )
    except Exception as exc:
        logger.error("Réponse Gemini inattendue pour le budget : %s", data)
        raise HTTPException(status_code=500, detail="Réponse IA mal formée.") from exc
