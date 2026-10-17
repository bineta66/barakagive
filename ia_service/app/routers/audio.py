import logging
import os
from pathlib import PurePath

import httpx
from fastapi import APIRouter, HTTPException, Request

logger = logging.getLogger(__name__)
router = APIRouter()

_ALLOWED_TYPES = {
    "audio/webm": ".webm",
    "audio/ogg": ".ogg",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/mpeg": ".mp3",
    "audio/mp3": ".mp3",
    "audio/mp4": ".m4a",
    "audio/x-m4a": ".m4a",
}


@router.post("/audio/transcribe")
async def transcribe_audio(request: Request):
    """Transcribe a short voice note. Audio and transcript are never logged or stored here."""
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(status_code=503, detail="La transcription vocale n’est pas configurée.")

    max_bytes = max(1, int(os.getenv("AI_AUDIO_MAX_BYTES", str(15 * 1024 * 1024))))
    max_duration = max(1, int(os.getenv("AI_AUDIO_MAX_DURATION_SECONDS", "120")))
    try:
        duration = int(request.headers.get("X-Audio-Duration-Seconds", "0"))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Durée audio invalide.") from exc
    if duration < 1 or duration > max_duration:
        raise HTTPException(status_code=400, detail=f"La durée audio doit être comprise entre 1 et {max_duration} secondes.")

    media_type = request.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
    extension = _ALLOWED_TYPES.get(media_type)
    if not extension:
        raise HTTPException(status_code=415, detail="Format audio non pris en charge.")

    try:
        content_length = int(request.headers.get("Content-Length", "0"))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Taille audio invalide.") from exc
    if content_length > max_bytes:
        raise HTTPException(status_code=413, detail="Le fichier audio est trop volumineux. Enregistrez un message plus court.")
    content = bytearray()
    async for chunk in request.stream():
        if len(content) + len(chunk) > max_bytes:
            raise HTTPException(status_code=413, detail="Le fichier audio est trop volumineux. Enregistrez un message plus court.")
        content.extend(chunk)
    if not content:
        raise HTTPException(status_code=400, detail="Le fichier audio est vide.")
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail="Le fichier audio est trop volumineux. Enregistrez un message plus court.")

    raw_filename = request.headers.get("X-Audio-Filename", "message-vocal" + extension)
    filename = PurePath(raw_filename.replace("\\", "/")).name
    if not filename.lower().endswith(extension):
        filename = "message-vocal" + extension

    base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")
    model = os.getenv("GROQ_STT_MODEL", "whisper-large-v3-turbo")
    timeout = max(5.0, float(os.getenv("AI_REQUEST_TIMEOUT", "60")))
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{base_url}/audio/transcriptions",
                headers={"Authorization": f"Bearer {api_key}"},
                data={"model": model, "response_format": "json", "temperature": "0"},
                files={"file": (filename, bytes(content), media_type)},
            )
    except httpx.TimeoutException as exc:
        logger.warning("Voice transcription timed out (model=%s)", model)
        raise HTTPException(status_code=503, detail="La transcription a dépassé le délai. Réessayez avec un message plus court.") from exc
    except httpx.HTTPError as exc:
        logger.warning("Voice transcription provider unavailable (%s)", type(exc).__name__)
        raise HTTPException(status_code=503, detail="La transcription vocale est temporairement indisponible.") from exc

    if response.is_error:
        logger.warning("Voice transcription provider returned status=%s", response.status_code)
        raise HTTPException(status_code=503, detail="La transcription vocale a échoué. Réessayez.")
    try:
        transcript = response.json().get("text", "").strip()
    except (ValueError, AttributeError) as exc:
        raise HTTPException(status_code=502, detail="Le service de transcription a renvoyé une réponse invalide.") from exc
    if not transcript:
        raise HTTPException(status_code=422, detail="Je n’ai pas réussi à comprendre clairement votre message vocal. Pouvez-vous réessayer ?")
    if len(transcript) > 4000:
        raise HTTPException(status_code=413, detail="La transcription dépasse la longueur maximale. Enregistrez un message plus court.")
    return {"transcription": transcript, "model": model}
