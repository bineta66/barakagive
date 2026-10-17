import os

from app.services.providers.base import AIErrorType, AIProviderError, error_from_status


class GeminiProvider:
    name = "gemini"

    def __init__(self, model):
        self.model = model
        self.model_name = os.getenv("GEMINI_MODEL", "models/gemini-flash-latest")

    def is_enabled(self) -> bool:
        return os.getenv("GEMINI_ENABLED", "true").lower() in {"1", "true", "yes", "on"} and self.model is not None

    def generate(self, prompt: str, *, timeout: float) -> str:
        try:
            response = self.model.generate_content(prompt, request_options={"timeout": timeout})
        except Exception as exc:
            status = getattr(exc, "status_code", None) or getattr(exc, "code", None)
            if not isinstance(status, int):
                response_obj = getattr(exc, "response", None)
                status = getattr(response_obj, "status_code", None)
            if isinstance(status, int):
                raise error_from_status(status) from exc
            name = type(exc).__name__.lower()
            if "timeout" in name or "deadline" in name:
                raise AIProviderError(AIErrorType.TIMEOUT) from exc
            if any(term in name for term in ("connection", "network", "transport")):
                raise AIProviderError(AIErrorType.NETWORK_ERROR) from exc
            raise AIProviderError(AIErrorType.UNKNOWN_ERROR) from exc
        content = getattr(response, "text", None)
        if not content:
            raise AIProviderError(AIErrorType.INVALID_RESPONSE, "Empty Gemini response")
        return content
