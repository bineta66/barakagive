import os

from app.services.providers.openai_compatible import OpenAICompatibleProvider


class OpenRouterProvider(OpenAICompatibleProvider):
    name = "openrouter"
    key_env = "OPENROUTER_API_KEY"
    model_env = "OPENROUTER_MODEL"
    base_url_env = "OPENROUTER_BASE_URL"
    default_base_url = "https://openrouter.ai/api/v1"

    def __init__(self):
        super().__init__()
        self.model_name = os.getenv("OPENROUTER_MODEL", "")
