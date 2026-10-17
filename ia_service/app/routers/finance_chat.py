from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing import Any, Dict, Optional
from app.services.gemini_service import gemini_service
from app.schemas.security import TrustedTenant
from app.guardrails import input_guardrail_message, out_of_scope_message, sanitize_model_output, redact_personal_data

router = APIRouter()


class FinanceChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1, max_length=4000)
    context: Dict[str, Any]
    tenant: TrustedTenant

    @field_validator("question")
    @classmethod
    def strip_question(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("La question ne peut pas être vide.")
        return value

    @model_validator(mode="after")
    def allow_finance_roles_only(self):
        if self.tenant.role not in {"GERANT", "FINANCE", "SUPER_ADMIN"}:
            raise ValueError("Rôle non autorisé pour l'assistant Finance.")
        return self


class FinanceChatResponse(BaseModel):
    answer: str
    alert: Optional[str] = "GREEN"
    generated_at: str


@router.post("/finance-chat", response_model=FinanceChatResponse)
async def finance_chat(request: FinanceChatRequest):
    """
    Assistant IA conversationnel pour le Responsable Finance.
    Reçoit une question + contexte financier réel Django + historique.
    Retourne une réponse en langage naturel avec niveau d'alerte.
    """
    blocked = input_guardrail_message(request.question)
    if blocked:
        return {"answer": blocked, "alert": "GREEN", "generated_at": datetime.utcnow().isoformat() + "Z"}
    out_of_scope = out_of_scope_message(request.question)
    if out_of_scope:
        return {"answer": out_of_scope, "alert": "GREEN", "generated_at": datetime.utcnow().isoformat() + "Z"}
    try:
        result = await run_in_threadpool(
            gemini_service.analyze_finance_chat,
            question=request.question,
            context=request.context,
            history=[],
        )
        return {
            "answer": redact_personal_data(sanitize_model_output(result.get("answer", "Je n'ai pas pu générer une réponse."))),
            "alert":        result.get("alert", "GREEN"),
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur interne du service IA.")
