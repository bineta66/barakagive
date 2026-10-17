import httpx

from app.services.providers.base import AIErrorType, AIProviderError, error_from_status


class OpenAICompatibleProvider:
    name = ""
    key_env = ""
    model_env = ""
    base_url_env = ""
    default_base_url = ""

    def __init__(self):
        import os
        self.api_key = os.getenv(self.key_env, "")
        self.model_name = os.getenv(self.model_env, "")
        self.base_url = os.getenv(self.base_url_env, self.default_base_url).rstrip("/")

    def is_enabled(self) -> bool:
        import os
        return os.getenv(f"{self.name.upper()}_ENABLED", "true").lower() in {"1", "true", "yes", "on"} and bool(self.api_key and self.model_name)

    def generate(self, prompt: str, *, timeout: float) -> str:
        if not self.api_key or not self.model_name:
            raise AIProviderError(AIErrorType.CONFIGURATION_ERROR)
        try:
            response = httpx.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": self.model_name, "messages": [{"role": "user", "content": prompt}]},
                timeout=timeout,
            )
        except httpx.TimeoutException as exc:
            raise AIProviderError(AIErrorType.TIMEOUT) from exc
        except httpx.NetworkError as exc:
            raise AIProviderError(AIErrorType.NETWORK_ERROR) from exc
        except httpx.HTTPError as exc:
            raise AIProviderError(AIErrorType.NETWORK_ERROR) from exc
        if response.is_error:
            raise error_from_status(response.status_code)
        try:
            content = response.json()["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise AIProviderError(AIErrorType.INVALID_RESPONSE) from exc
        if not isinstance(content, str) or not content.strip():
            raise AIProviderError(AIErrorType.INVALID_RESPONSE)
        return content
