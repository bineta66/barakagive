from datetime import datetime
from fastapi import APIRouter, HTTPException, status
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
        raise HTTPException(status_code=500, detail="Erreur interne du service IA.")


@router.get("/budget-analysis/{campagne_id}")
async def get_budget_analysis(campagne_id: str):
    """The IA service has no authorized source for finance data on GET."""
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="Transmettez les données financières vérifiées par Django avec POST.",
    )
