import logging

from fastapi import HTTPException

logger = logging.getLogger(__name__)


def parse_json_response(raw: str) -> dict:
    try:
        import json
        return json.loads(raw)
    except Exception as exc:
        logger.error("Réponse Gemini invalide : %s", raw)
        raise HTTPException(status_code=500, detail="Réponse IA invalide.") from exc
