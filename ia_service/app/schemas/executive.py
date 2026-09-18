from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AlertLevel(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    ORANGE = "ORANGE"
    RED = "RED"


class UrgencyLevel(str, Enum):
    FAIBLE = "Faible"
    MOYENNE = "Moyenne"
    ELEVEE = "Élevée"
    TRES_ELEVEE = "Très élevée"
    CRITIQUE = "Critique"


class CampaignPrioritaire(BaseModel):
    id: str
    nom: str
    region: str
    urgence: UrgencyLevel
    beneficiares_count: int = Field(alias="beneficiaires_count")
    score: float


class ZonePrioritaire(BaseModel):
    id: str
    nom: str
    region: str
    score: float
    beneficiaires: int
    niveau_urgence: UrgencyLevel


class BudgetGlobal(BaseModel):
    total: float
    taux: float
    solde: float
    alerte: bool


class ExecutiveInsightResponse(BaseModel):
    resume: str
    alert: AlertLevel
    campagne_prioritaire: Optional[CampaignPrioritaire] = None
    zone_prioritaire: Optional[ZonePrioritaire] = None
    budget: Optional[BudgetGlobal] = None
    recommandations: List[str] = []
    generated_at: datetime


# Request schemas
class CampaignBase(BaseModel):
    campagne_id: str
    nom: str


class ExecutiveAnalyzeRequest(CampaignBase):
    campaigns: List[Dict[str, Any]] = []
    beneficiaries: List[Dict[str, Any]] = []
    zones: List[Dict[str, Any]] = []
    budgets: List[Dict[str, Any]] = []
    expenses: List[Dict[str, Any]] = []