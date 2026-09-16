from fastapi import APIRouter
from app.schemas.common import HealthResponse
from app.core.config import MODEL_NAME

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", service="BarakaGive360 IA", model=MODEL_NAME)
