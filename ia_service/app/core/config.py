import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")

if not GEMINI_API_KEY:
    raise RuntimeError("La variable d'environnement GEMINI_API_KEY est requise.")
