from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class UrgencyLevel(str, Enum):
    FAIBLE = "Faible"
    MOYENNE = "Moyenne"
    ELEVEE = "Élevée"
    TRES_ELEVEE = "Très élevée"
    CRITIQUE = "Critique"


class VulnerabilityLevel(str, Enum):
    TRES_ELEVEE = "TRES_ELEVEE"
    ELEVEE = "ELEVEE"
    MOYENNE = "MOYENNE"
    FAIBLE = "FAIBLE"
    AUCUNE_DONNEE = "AUCUNE_DONNEE"


class ZoneData(BaseModel):
    name: str
    score: float
    beneficiaries: int
    level: VulnerabilityLevel
    zone_id: Optional[str] = None


class RegionAnalysisRequest(BaseModel):
    region: str
    campaign: str
    total_beneficiaries: int
    zones_count: int
    zones: List[ZoneData]


class ZoneAnalysisItem(BaseModel):
    zone: str
    summary: str


class RegionAnalysisResponse(BaseModel):
    executive_summary: str
    zone_analysis: List[ZoneAnalysisItem]
    recommendations: List[str]
    generated_at: str


class ZoneRankingItem(BaseModel):
    rang: int
    zone: str
    id: str
    score_total: float
    beneficiaires: int
    niveau_urgence: UrgencyLevel
    region: str
    departement: str


class RegionZonesResponse(BaseModel):
    region: str
    zones: List[ZoneRankingItem]


class ZoneDetailResponse(BaseModel):
    id: str
    nom: str
    region: str
    departement: str
    niveau: UrgencyLevel
    score_total: float
    beneficiaires: int
    justification: str
    recommandation: str
    top5_beneficiaires: List[Dict]
    generated_at: datetime


class AnalyzeAllRequest(BaseModel):
    campagne_id: str
    nom: str