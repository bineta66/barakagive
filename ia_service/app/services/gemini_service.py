import os
from google import genai
from google.genai import types

from app.core.config import GEMINI_API_KEY, MODEL_NAME
from app.services.prompt_builder import build_prompt


_client = genai.Client(api_key=GEMINI_API_KEY)


def call_gemini(data: dict) -> str:
    prompt = build_prompt(data)
    response = _client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json",
        ),
    )
    return response.candidates[0].content.parts[0].text
