from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.schemas import ExecutiveInsightResponse, ExecutiveAnalyzeRequest
from app.services.gemini_service import gemini_service

router = APIRouter()


@router.post("/executive-insight", response_model=ExecutiveInsightResponse)
async def get_executive_insight(request: ExecutiveAnalyzeRequest):
    """Analyse stratégique pour le Gérant - Executive Orbital IA"""
    try:
        result = gemini_service.analyze_executive(request.model_dump())
        result["generated_at"] = datetime.utcnow().isoformat()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur interne du service IA.")
