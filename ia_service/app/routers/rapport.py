from fastapi import APIRouter
from typing import Dict, Any
from app.services.gemini_service import gemini_service

router = APIRouter()

@router.post("/generate")
def generate_report(data: Dict[str, Any]):
    """
    Génère un rapport d'activité, financier et d'impact via Gemini.
    """
    try:
        report = gemini_service.generate_report(data)
        return {"report": report}
    except Exception as e:
        return {"error": str(e)}
