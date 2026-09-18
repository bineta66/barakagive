from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.schemas import ExecutiveAnalyzeRequest
from app.services.gemini_service import gemini_service

router = APIRouter()


@router.post("/analyze-all")
async def analyze_all(request: ExecutiveAnalyzeRequest):
    """
    Endpoint appelé par le cron job Django toutes les 6h.
    Déclenche toutes les analyses pour une campagne active.
    """
    try:
        campagne_id = request.campagne_id
        
        # 1. Executive Insight
        executive_result = gemini_service.analyze_executive(request.model_dump())
        
        # 2. Zones Analysis
        zones_result = gemini_service.analyze_zones(request.model_dump())
        
        # 3. Finance Analysis
        finance_result = gemini_service.analyze_finance(request.model_dump())
        
        # Combine all results
        combined = {
            "executive": executive_result,
            "zones_prioritaires": zones_result.get("zones_prioritaires", []),
            "finance": finance_result,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return combined
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))