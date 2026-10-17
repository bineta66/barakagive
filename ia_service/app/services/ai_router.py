import logging
import os
import time
import uuid
from dataclasses import dataclass

from app.services.providers.base import AIProviderError, AIResponse
from app.services.providers.groq_provider import GroqProvider
from app.services.providers.openrouter_provider import OpenRouterProvider
from app.guardrails import sanitize_model_output

logger = logging.getLogger(__name__)


@dataclass
class _ProviderState:
    failures: int = 0
    unavailable_until: float = 0


class AIRouter:
    def __init__(self, providers):
        self.providers = {provider.name: provider for provider in providers}
        self.states = {name: _ProviderState() for name in self.providers}

    def generate(self, prompt: str, *, operation: str = "generation", request_id: str | None = None) -> str:
        return self.generate_response(prompt, operation=operation, request_id=request_id).content

    def generate_response(self, prompt: str, *, operation: str = "generation", request_id: str | None = None) -> AIResponse:
        request_id = request_id or str(uuid.uuid4())
        order = [name.strip().lower() for name in os.getenv("AI_PROVIDER_ORDER", "gemini,groq,openrouter").split(",") if name.strip()]
        timeout = max(0.1, float(os.getenv("AI_REQUEST_TIMEOUT", "60")))
        retries = max(0, int(os.getenv("AI_MAX_RETRIES", "1")))
        cooldown = max(0, int(os.getenv("AI_PROVIDER_COOLDOWN_SECONDS", "60")))
        threshold = max(1, int(os.getenv("AI_CIRCUIT_FAILURE_THRESHOLD", "3")))
        enabled = [self.providers[name] for name in order if name in self.providers and self.providers[name].is_enabled()]
        if not enabled:
            raise RuntimeError("Le service IA est indisponible : aucun fournisseur n'est configuré.")

        last_error = None
        tried = 0
        for index, provider in enumerate(enabled):
            state = self.states[provider.name]
            if state.unavailable_until > time.monotonic():
                logger.info("[AI] request_id=%s operation=%s provider=%s status=cooldown fallback=%s", request_id, operation, provider.name, index > 0)
                continue
            tried += 1
            for attempt in range(retries + 1):
                start = time.monotonic()
                try:
                    content = provider.generate(prompt, timeout=timeout)
                    latency = int((time.monotonic() - start) * 1000)
                    state.failures = 0
                    state.unavailable_until = 0
                    logger.info("[AI] request_id=%s operation=%s provider=%s model=%s status=success latency_ms=%d fallback=%s", request_id, operation, provider.name, provider.model_name, latency, index > 0)
                    return AIResponse(sanitize_model_output(content), provider.name, provider.model_name, request_id, latency)
                except AIProviderError as exc:
                    latency = int((time.monotonic() - start) * 1000)
                    last_error = exc
                    logger.warning("[AI] request_id=%s operation=%s provider=%s status=%s error_type=%s latency_ms=%d fallback=%s", request_id, operation, provider.name, exc.status or exc.error_type.value, exc.error_type.value, latency, index > 0)
                    if not exc.retryable:
                        raise RuntimeError("Le fournisseur IA a refusé la requête.") from exc
                    state.failures += 1
                    if state.failures >= threshold and cooldown:
                        state.unavailable_until = time.monotonic() + cooldown
                    if attempt < retries:
                        continue
                    break
            if last_error and not last_error.retryable:
                break
        if tried == 0:
            raise RuntimeError("Tous les fournisseurs IA sont temporairement en cooldown.")
        raise RuntimeError("Tous les fournisseurs IA sont temporairement indisponibles.") from last_error


def create_ai_router(gemini_model):
    from app.services.providers.gemini_provider import GeminiProvider
    return AIRouter([GeminiProvider(gemini_model), GroqProvider(), OpenRouterProvider()])
