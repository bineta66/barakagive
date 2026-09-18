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
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executive-insight")
async def get_executive_insight_get():
    """GET endpoint for frontend compatibility - uses mock data if no campaign specified"""
    try:
        # Return mock/default data for GET requests
        result = gemini_service.analyze_executive({
            "campagne_id": "default",
            "nom": "Campagne active",
            "campaigns": [],
            "beneficiaries": [],
            "zones": [],
            "budgets": [],
            "expenses": []
        })
        result["generated_at"] = datetime.utcnow().isoformat()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))