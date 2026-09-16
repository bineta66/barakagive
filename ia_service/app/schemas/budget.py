from pydantic import BaseModel


class Depense(BaseModel):
    date: str
    categorie: str
    montant: float
    zone: str | None = None


class BudgetRequest(BaseModel):
    projet: str
    budget_total: float
    dons_recus: float
    depenses_totales: float
    solde: float
    taux_execution: int
    depenses: list[Depense]


class BudgetResponse(BaseModel):
    generated_at: str
    resume: str
    alerte: str
    zone_plus_depensiere: str
    categorie_plus_depensiere: str
    recommandation: str
