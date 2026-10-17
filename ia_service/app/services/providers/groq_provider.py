import os

from app.services.providers.openai_compatible import OpenAICompatibleProvider


class GroqProvider(OpenAICompatibleProvider):
    name = "groq"
    key_env = "GROQ_API_KEY"
    model_env = "GROQ_MODEL"
    base_url_env = "GROQ_BASE_URL"
    default_base_url = "https://api.groq.com/openai/v1"

    def __init__(self):
        super().__init__()
        self.model_name = os.getenv("GROQ_MODEL", "")
