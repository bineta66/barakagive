from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.schemas import BudgetAnalysisResponse, FinanceAnalyzeRequest
from app.services.gemini_service import gemini_service

router = APIRouter()


@router.post("/budget-analysis/{campagne_id}", response_model=BudgetAnalysisResponse)
async def analyze_budget(campagne_id: str, request: FinanceAnalyzeRequest):
    """Analyse budgétaire pour le Responsable Finance - Financial Orbital"""
    try:
        data = request.model_dump()
        data["campagne_id"] = campagne_id
        result = gemini_service.analyze_finance(data)
        result["generated_at"] = datetime.utcnow().isoformat()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/budget-analysis/{campagne_id}")
async def get_budget_analysis(campagne_id: str):
    """GET endpoint for frontend"""
    try:
        # For GET, we need to fetch data from Django. 
        # For now return mock - in production this would call Django backend
        result = gemini_service.analyze_finance({
            "campagne_id": campagne_id,
            "nom": f"Campagne {campagne_id}",
            "budget_total": 50000000,
            "depenses_totales": 34000000,
            "solde": 16000000,
            "taux_execution": 68.0,
            "date_cloture": "2025-12-31",
            "jours_restants": 45,
            "depenses_par_zone": [],
            "depenses_par_categorie": []
        })
        result["generated_at"] = datetime.utcnow().isoformat()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))