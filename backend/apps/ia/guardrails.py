"""Small, conservative guardrails for conversational AI input and audit text."""
import re
import unicodedata


_INJECTION_PATTERNS = (
    re.compile(r"\bignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions\b", re.I),
    re.compile(r"\b(?:reveal|show|print|repeat|display)\b.{0,50}\b(?:system prompt|hidden prompt|internal instructions|secret|credentials|api key|token)\b", re.I),
    re.compile(r"\b(?:ignore|oublie|ignorer|efface)\b.{0,60}\b(?:instructions? pr[eé]c[eé]dentes?|consignes? pr[eé]c[eé]dentes?|r[eè]gles? du syst[eè]me)\b", re.I),
    re.compile(r"\b(?:affiche|r[eé]v[eè]le|donne|imprime|copie)\b.{0,60}\b(?:prompt syst[eè]me|instructions internes|cl[eé]s? secr[eè]tes?|identifiants|api[_ -]?key|jeton d'acc[eè]s)\b", re.I),
)
_SECRET_PATTERNS = (
    re.compile(r"(?i)\b(?:api[_ -]?key|secret[_ -]?(?:key|token)|access[_ -]?token|password|mot de passe)\s*[:=]\s*[^\s,;]+"),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{12,}"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bAIza[A-Za-z0-9_-]{30,}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)


def input_guardrail_message(text):
    """Return a refusal only for explicit prompt extraction/injection attempts."""
    value = unicodedata.normalize("NFKD", str(text or "").casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    if any(pattern.search(value) for pattern in _INJECTION_PATTERNS):
        return ("Je ne peux pas divulguer les instructions internes, les identifiants ou les données d'une autre organisation. "
                "Je peux vous aider avec les projets, campagnes, bénéficiaires, zones et finances autorisés dans BarakaGive360.")
    if any(pattern.search(value) for pattern in _SECRET_PATTERNS):
        return "Votre message semble contenir un secret ou un identifiant. Supprimez sa valeur et renvoyez votre question sans la clé, le jeton ou le mot de passe."
    return None


def out_of_scope_message(text):
    from apps.ia.assistant_intents import OUT_OF_SCOPE_REPLY, classify_assistant_intent

    return OUT_OF_SCOPE_REPLY if classify_assistant_intent(text) == "OUT_OF_SCOPE" else None


def redact_sensitive_text(text):
    value = str(text or "")
    for pattern in _SECRET_PATTERNS:
        value = pattern.sub("[secret masqué]", value)
    return value


def safe_audit_text(text, limit=2000):
    """Keep useful audit text while removing credentials and common contact PII."""
    value = str(text or "")
    for pattern in _SECRET_PATTERNS:
        value = pattern.sub("[secret masqué]", value)
    try:
        from django.conf import settings

        for name in (
            "SECRET_KEY", "AI_SERVICE_TOKEN", "AI_CONTEXT_SIGNING_KEY",
            "GEMINI_API_KEY", "GROQ_API_KEY", "OPENROUTER_API_KEY",
        ):
            secret = str(getattr(settings, name, "") or "")
            if len(secret) >= 8:
                value = value.replace(secret, "[secret masqué]")
    except Exception:
        # Keep the utility usable in isolated tests and management contexts.
        pass
    value = re.sub(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", "[email masque]", value)
    value = re.sub(r"(?i)(?<!\w)(?:\+?221[ .-]?)?7(?:[ .-]?\d){8}(?!\w)(?!\s*(?:FCFA|XOF|EUR|USD))", "[telephone masque]", value)
    value = re.sub(r"(?i)(?<!\w)0(?:[ .-]?\d){9}(?!\w)(?!\s*(?:FCFA|XOF|EUR|USD))", "[telephone masque]", value)
    value = re.sub(r"(?i)\b(?:adresse|address)\s*[:=]\s*[^,;\n]{5,100}", "adresse [masquee]", value)
    return value[:limit]
