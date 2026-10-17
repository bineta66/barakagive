from fastapi import FastAPI, Depends

from app.security import require_internal_service_token
from app.routers import executive, zones, finance, analyze, chat, finance_chat, rapport, verification, forms, audio

app = FastAPI(
    title="BarakaGive360 IA Service",
    description="Service d'intelligence artificielle pour BarakaGive360 - Gemini 2.5 Flash",
    version="1.0.0",
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
)

internal = [Depends(require_internal_service_token)]

app.include_router(executive.router, prefix="/api/ia", tags=["executive"], dependencies=internal)
app.include_router(zones.router, prefix="/api/ia", tags=["zones"], dependencies=internal)
app.include_router(finance.router, prefix="/api/ia", tags=["finance"], dependencies=internal)
app.include_router(analyze.router, prefix="/api/ia", tags=["analyze"], dependencies=internal)
app.include_router(chat.router, prefix="/api/ia", tags=["chat"], dependencies=internal)
app.include_router(forms.router, prefix="/api/ia", tags=["forms"], dependencies=internal)
app.include_router(audio.router, prefix="/api/ia", tags=["audio"], dependencies=internal)
app.include_router(finance_chat.router, prefix="/api/ia", tags=["finance-chat"], dependencies=internal)
app.include_router(rapport.router, prefix="/api/ia/rapport", tags=["rapport"], dependencies=internal)
app.include_router(verification.router, prefix="/api/ia/verification", tags=["verification"], dependencies=internal)
app.include_router(verification.router, prefix="/api/ia/ocr", tags=["ocr"], dependencies=internal)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "ia_service"}
