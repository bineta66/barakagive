import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.schemas.priorisation import PriorisationRequest, PriorisationResponse
from app.services.gemini_service import call_gemini
from app.services.response_parser import parse_json_response

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/api/ia/priorisation", response_model=PriorisationResponse)
async def prioriser(request: PriorisationRequest):
    if request.campagne.statut.upper() != "ACTIVE":
        raise HTTPException(status_code=400, detail="Campagne non active.")

    try:
        raw = call_gemini(request.model_dump())
        data = parse_json_response(raw)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Erreur lors de l'appel à Gemini pour la priorisation.")
        raise HTTPException(status_code=500, detail="Erreur du service IA.") from exc

    try:
        return PriorisationResponse(
            generated_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            resume=data.get("resume", ""),
            zone_recommandee=data.get("zone_recommandee", ""),
            justification=data.get("justification", ""),
            recommandation=data.get("recommandation", ""),
            zones=[],
        )
    except Exception as exc:
        logger.error("Réponse Gemini inattendue : %s", data)
        raise HTTPException(status_code=500, detail="Réponse IA mal formée.") from exc
