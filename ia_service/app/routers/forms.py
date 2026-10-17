import json
import re
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.gemini_service import gemini_service

router = APIRouter()


class FormCriteria(BaseModel):
    id: int | str
    nom: str = Field(min_length=1, max_length=200)
    poids: int = Field(ge=0, le=100)


class FormQuestionsRequest(BaseModel):
    projet: str = Field(min_length=1, max_length=200)
    campagne: str = Field(min_length=1, max_length=200)
    criteres: list[FormCriteria] = Field(min_length=1, max_length=30)


@router.post("/form-questions")
def generate_form_questions(request: FormQuestionsRequest) -> dict[str, Any]:
    criteria = [item.model_dump() for item in request.criteres]
    prompt = f"""
Tu aides un chef de projet humanitaire à concevoir un formulaire de collecte.
Projet : {request.projet}
Campagne : {request.campagne}
Critères et poids fournis par le projet : {json.dumps(criteria, ensure_ascii=False)}

Tâche : rédige un résumé de 2 ou 3 phrases expliquant comment ces critères guideront
l'évaluation de vulnérabilité, puis exactement 3 questions utiles et neutres pour CHAQUE critère.
N'invente aucun critère ni poids. Les questions doivent être compréhensibles par un agent de terrain.

Retourne UNIQUEMENT un objet JSON valide, sans markdown, au format exact :
{{"resume":"...","questions":[{{"critere_id":{json.dumps(criteria[0]['id'])},"question":"...","type":"YES_NO","options":[],"aide":"..."}}]}}
Chaque entrée doit contenir critere_id, question, type, options et aide.
Types autorisés : TEXT, TEXTAREA, NUMBER, DATE, YES_NO, RADIO, CHECKBOX, SELECT,
PHONE, EMAIL, PHOTO, FILE, GPS, SCALE.
Pour RADIO, CHECKBOX et SELECT, donne au moins deux options pertinentes.
"""
    try:
        answer = gemini_service._call_gemini(prompt, operation="form_questions")
        match = re.search(r"\{.*\}", answer, flags=re.DOTALL)
        if not match:
            raise ValueError("JSON absent")
        payload = json.loads(match.group(0))
        criterion_ids = {str(item.id) for item in request.criteres}
        valid_types = {"TEXT", "TEXTAREA", "NUMBER", "DATE", "YES_NO", "RADIO", "CHECKBOX", "SELECT", "PHONE", "EMAIL", "PHOTO", "FILE", "GPS", "SCALE"}
        questions = []
        for item in payload.get("questions", []):
            if not isinstance(item, dict) or str(item.get("critere_id")) not in criterion_ids:
                continue
            if item.get("type") not in valid_types or not str(item.get("question", "")).strip():
                continue
            options = item.get("options", [])
            if not isinstance(options, list):
                options = []
            if item["type"] in {"RADIO", "CHECKBOX", "SELECT"} and len(options) < 2:
                options = ["Oui", "Non"]
            questions.append({
                "critere_id": str(item["critere_id"]),
                "question": str(item["question"])[:300],
                "type": item["type"],
                "options": [str(option)[:100] for option in options[:20]],
                "aide": str(item.get("aide", ""))[:500],
            })
        if not questions:
            raise ValueError("Aucune question exploitable")
        return {"resume": str(payload.get("resume", ""))[:1200], "questions": questions}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Génération IA indisponible ou réponse invalide.") from exc
