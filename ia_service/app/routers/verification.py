from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from app.services.gemini_service import gemini_service

router = APIRouter()


@router.post("/verify")
def verify_documents(data: Dict[str, Any]):
    """Verify ONG registration documents using the configured AI service."""
    try:
        return gemini_service.verify_ong_documents(data)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Le service de vérification des documents est indisponible.",
        )
