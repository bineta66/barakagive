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