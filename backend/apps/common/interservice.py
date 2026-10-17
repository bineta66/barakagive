import hashlib
import hmac
import json
import time
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def _json_default(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    raise TypeError(f"Type non sérialisable pour le service IA : {type(value).__name__}")


def ai_service_headers(body: bytes | None = None):
    """Return server-only authentication headers and optionally sign a body."""
    token = getattr(settings, "AI_SERVICE_TOKEN", "")
    if not token:
        raise ImproperlyConfigured("AI_SERVICE_TOKEN n'est pas configuré.")
    headers = {"X-Internal-Service-Token": token}
    if body is None:
        return headers

    signing_key = getattr(settings, "AI_CONTEXT_SIGNING_KEY", "")
    if not signing_key:
        raise ImproperlyConfigured("AI_CONTEXT_SIGNING_KEY n'est pas configurée.")
    timestamp = str(int(time.time()))
    signed_value = timestamp.encode("ascii") + b"." + body
    signature = hmac.new(signing_key.encode("utf-8"), signed_value, hashlib.sha256).hexdigest()
    headers.update({
        "X-Context-Timestamp": timestamp,
        "X-Context-Signature": signature,
    })
    return headers


def post_to_ai_service(url, *, payload=None, body=None, timeout=30, headers=None):
    """POST a JSON or binary body to FastAPI with service auth and body integrity."""
    if body is None:
        if payload is None:
            raise ValueError("Un payload ou un corps est requis pour un appel IA signé.")
        body = json.dumps(
            payload,
            default=_json_default,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    elif not isinstance(body, bytes):
        body = bytes(body)

    request_headers = {
        "Content-Type": "application/json" if payload is not None else "application/octet-stream",
        **(headers or {}),
        **ai_service_headers(body),
    }
    return requests.post(url, data=body, headers=request_headers, timeout=timeout)


def ai_tenant_identity(user):
    """Build tenant claims solely from the authenticated Django user record."""
    return {
        "organization_id": user.organization_id,
        "user_id": user.pk,
        "role": user.role,
    }
