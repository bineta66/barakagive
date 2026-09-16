from pydantic import BaseModel


class CampagneIA(BaseModel):
    id: int
    nom: str
    statut: str


class ProjetIA(BaseModel):
    id: int
    nom: str


class TopBeneficiaire(BaseModel):
    id: int
    nom: str
    score: int
    raisons: list[str]


class Zone(BaseModel):
    nom: str
    urgence: str
    score_total: int
    beneficiaires_prioritaires: int
    top5: list[TopBeneficiaire]


class PriorisationRequest(BaseModel):
    campagne: CampagneIA
    projet: ProjetIA
    zones: list[Zone]


class PriorisationResponse(BaseModel):
    generated_at: str
    resume: str
    zone_recommandee: str
    justification: str
    recommandation: str
    zones: list
