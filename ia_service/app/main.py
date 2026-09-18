from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import executive, zones, finance, analyze

app = FastAPI(
    title="BarakaGive360 IA Service",
    description="Service d'intelligence artificielle pour BarakaGive360 - Gemini 2.5 Flash",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(executive.router, prefix="/api/ia", tags=["executive"])
app.include_router(zones.router, prefix="/api/ia", tags=["zones"])
app.include_router(finance.router, prefix="/api/ia", tags=["finance"])
app.include_router(analyze.router, prefix="/api/ia", tags=["analyze"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "ia_service"}