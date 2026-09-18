from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.schemas import RegionZonesResponse, ZoneDetailResponse
from app.services.gemini_service import gemini_service

router = APIRouter()


@router.post("/regions/{region_id}/analyze", response_model=RegionZonesResponse)
async def analyze_region_zones(region_id: str, request: dict):
    """Analyse des zones pour une région - Chef de Projet"""
    try:
        data = request
        data["region"] = region_id
        result = gemini_service.analyze_zones(data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/regions/{region_id}/zones")
async def get_region_zones(region_id: str):
    """GET endpoint for frontend - returns zones for a region"""
    try:
        result = gemini_service.analyze_zones({"region": region_id})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/zones/{zone_id}/analyze", response_model=ZoneDetailResponse)
async def analyze_zone_detail(zone_id: str, request: dict):
    """Analyse détaillée d'une zone - Chef de Projet"""
    try:
        result = gemini_service.analyze_zone_detail(request, zone_id)
        result["generated_at"] = datetime.utcnow().isoformat()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/zones/{zone_id}")
async def get_zone_detail(zone_id: str):
    """GET endpoint for frontend - returns zone detail"""
    try:
        result = gemini_service.analyze_zone_detail({}, zone_id)
        result["generated_at"] = datetime.utcnow().isoformat()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))