from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class AlertLevel(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    ORANGE = "ORANGE"
    RED = "RED"


class BudgetAnalysisResponse(BaseModel):
    alert: AlertLevel
    resume: str
    prediction: str
    justification: str
    recommandation: str
    budget: float
    depenses: float
    solde: float
    taux_execution: float
    date_cloture: str
    jours_restants: int
    zone_plus_depensiere: str
    categorie_plus_depensiere: str
    generated_at: datetime


class FinanceAnalyzeRequest(BaseModel):
    campagne_id: str
    nom: str
    budget_total: float
    depenses_totales: float
    solde: float
    taux_execution: float
    date_cloture: str
    jours_restants: int
    depenses_par_zone: List[Dict] = []
    depenses_par_categorie: List[Dict] = []