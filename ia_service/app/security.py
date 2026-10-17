import hashlib
import hmac
import os
import time
from pathlib import Path

from fastapi import Header, HTTPException, Request, status
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


async def require_internal_service_token(
    request: Request,
    token: str | None = Header(default=None, alias="X-Internal-Service-Token"),
    context_timestamp: str | None = Header(default=None, alias="X-Context-Timestamp"),
    context_signature: str | None = Header(default=None, alias="X-Context-Signature"),
):
    """Authenticate Django and verify the integrity and freshness of its body."""
    expected = os.getenv("AI_SERVICE_TOKEN", "")
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="L'authentification interservice n'est pas configurée.",
        )
    if token is None or not hmac.compare_digest(token, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification interservice requise.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    signing_key = os.getenv("AI_CONTEXT_SIGNING_KEY", "")
    if not signing_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La signature des appels internes n'est pas configurée.",
        )
    try:
        if not context_timestamp or not context_timestamp.isascii() or not context_timestamp.isdecimal() or len(context_timestamp) > 12:
            raise ValueError
        issued_at = int(context_timestamp)
    except (TypeError, ValueError):
        issued_at = 0
    if not context_signature or abs(int(time.time()) - issued_at) > 300:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signature interne absente ou expirée.",
        )

    body = await request.body()
    signed_value = (context_timestamp or "").encode("ascii") + b"." + body
    expected_signature = hmac.new(
        signing_key.encode("utf-8"), signed_value, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(context_signature, expected_signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signature interne invalide.",
        )
