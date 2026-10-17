"""Defense-in-depth checks for conversational model inputs and outputs."""
import os
import re
import unicodedata

_DIRECT_SECRET_REQUEST = re.compile(
    r"(?i)\b(?:print|reveal|show|repeat|output|affiche|r[eé]v[eè]le|copie|donne|"
    r"here are|provide|voici)\b"
    r".{0,80}\b(?:api[_ -]?key|secret|password|mot de passe|token|jeton|credential|identifiant|"
    r"system prompt|hidden prompt|hidden system instructions|internal instructions|instructions internes|prompt systeme|regles du systeme)\b"
)
_CREDENTIAL_EXTRACTION_REQUEST = re.compile(
    r"(?i)\b(?:show|print|reveal|give|tell me|display|provide|affiche|donne|revele|copie|imprime|dis moi)\b"
    r".{0,80}\b(?:password|mot de passe|api[_ -]?key|cle api|secret|credential|identifiant|token|jeton|jwt)\b"
)
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

_ADDITIONAL_INJECTION_PATTERNS = (
    re.compile(r"(?i)\b(?:disregard|forget|bypass|override|ignore)\b.{0,100}\b(?:rules|guardrails|safety|instructions|restrictions|permissions)\b"),
    re.compile(r"(?i)\b(?:repeat|reveal|print|show|copy|quote|extract)\b.{0,100}\b(?:developer|system|hidden|private|internal)\b.{0,40}\b(?:prompt|message|instructions|rules)\b"),
    re.compile(r"(?i)\b(?:ignore|oublie|contourne|desactive)\b.{0,100}\b(?:regles|garde[- ]fous|securite|consignes|permissions|instructions)\b"),
    re.compile(r"(?i)\b(?:repete|revele|affiche|copie|extrais|cite)\b.{0,100}\b(?:prompt|message|instructions|regles)\b.{0,40}\b(?:systeme|prive|interne|cache)\b"),
)

def input_guardrail_message(text):
    value = str(text or "")
    normalized = unicodedata.normalize("NFKD", value.casefold())
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    if _CREDENTIAL_EXTRACTION_REQUEST.search(normalized) or any(
        pattern.search(normalized) for pattern in (*_INJECTION_PATTERNS, *_ADDITIONAL_INJECTION_PATTERNS)
    ):
        return ("Je ne peux pas divulguer les instructions internes, les identifiants ou les données d'une autre organisation. "
                "Je peux vous aider avec les projets, campagnes, bénéficiaires, zones et finances autorisés dans BarakaGive360.")
    if any(pattern.search(value) for pattern in _SECRET_PATTERNS):
        return "Votre message semble contenir un secret ou un identifiant. Supprimez sa valeur et renvoyez votre question sans la clé, le jeton ou le mot de passe."
    return None


def out_of_scope_message(text):
    value = unicodedata.normalize("NFKD", str(text or "").casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    allowed_topics = (
        "ong", "projet", "campagne", "beneficiair", "zone", "financ", "budget", "depens",
        "taux", "solde", "montant", "prevision", "risque", "justificatif", "depassement", "paiement",
        "bailleur", "subvention", "humanitaire", "barakagive", "token", "jeton", "api",
        "rag", "assistant", "intelligence artificielle", "secur", "cle", "identifiant",
        "donnee", "rapport", "alerte", "equipe", "activite", "financement", "association",
        "organisation", "programme", "intervention", "vulnerabilite", "fonds", "fournisseur",
        "application", "interface", "utiliser", "fonction", "compte",
        "mot de passe", "vocal", "audio", "transcription",
    )
    tokens = re.findall(r"[a-z0-9]+", value)
    exact_topics = {"ong", "don", "dons", "token", "jeton", "api", "rag", "assistant", "ia"}
    if any(
        token == topic or (topic not in exact_topics and token.startswith(topic))
        for topic in allowed_topics for token in tokens
    ):
        return None
    if value.strip(" .!?\n\t") in {"bonjour", "bonsoir", "salut", "salam", "merci", "ca va", "aide-moi", "aide moi", "resume", "synthese", "bilan", "question"}:
        return None
    return "Je peux vous aider sur BarakaGive360 : les ONG, projets, campagnes, bénéficiaires, zones, finances et le fonctionnement de l'assistant IA."


def sanitize_model_output(text):
    """Mask common credential formats and configured service credentials."""
    value = str(text or "")
    for pattern in _SECRET_PATTERNS:
        value = pattern.sub("[secret masqué]", value)
    for name in (
        "AI_SERVICE_TOKEN", "AI_CONTEXT_SIGNING_KEY", "GEMINI_API_KEY",
        "GROQ_API_KEY", "OPENROUTER_API_KEY",
    ):
        secret = os.getenv(name, "")
        if len(secret) >= 8:
            value = value.replace(secret, "[secret masqué]")
    if _DIRECT_SECRET_REQUEST.search(value):
        return ("Je ne peux pas divulguer de clé, de jeton, de mot de passe ou d'instruction interne. "
                "Je peux vous aider sur les données et fonctions autorisées de BarakaGive360.")
    return value


def redact_personal_data(text):
    """Remove common contact details from conversational text, preserving amounts and IDs."""
    value = str(text or "")
    value = re.sub(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", "[email masqué]", value)
    value = re.sub(r"(?i)(?<!\w)(?:\+?221[ .-]?)?7(?:[ .-]?\d){8}(?!\w)(?!\s*(?:FCFA|XOF|EUR|USD))", "[telephone masque]", value)
    value = re.sub(r"(?i)(?<!\w)0(?:[ .-]?\d){9}(?!\w)(?!\s*(?:FCFA|XOF|EUR|USD))", "[telephone masque]", value)
    value = re.sub(r"(?i)\b(?:adresse|address)\s*[:=]\s*[^,;\n]{5,100}", "adresse [masquée]", value)
    return value
