"""Intent classification for the executive assistant and project wizard."""
import re
import unicodedata
from difflib import SequenceMatcher


OUT_OF_SCOPE_REPLY = (
    "D\u00e9sol\u00e9, je suis l\u2019assistant ex\u00e9cutif de BarakaGive360. Je peux vous aider pour les questions concernant votre ONG, "
    "vos projets, vos campagnes, vos b\u00e9n\u00e9ficiaires, vos budgets et vos activit\u00e9s. Que souhaitez-vous faire ?"
)

BUSINESS_TERMS = (
    "ong", "organisation", "association", "projet", "campagne", "beneficiaire", "humanitaire",
    "budget", "finance", "financement", "depense", "don", "bailleur", "subvention", "activite",
    "equipe", "responsable", "zone", "region", "terrain", "rapport", "indicateur", "objectif",
)
SUMMARY_TERMS = ("bilan", "synthese", "situation de mon ong", "resume global", "vue d ensemble")
LIST_TERMS = ("liste", "quels projets", "mes projets", "affiche les projets", "voir les projets", "projets en cours")
EDIT_TERMS = ("corriger", "modifier", "changer", "rectifier", "mettre a jour")
QUESTION_STARTS = (
    "c est quoi", "qu est ce que", "que signifie", "que veut dire", "comment", "pourquoi",
    "combien", "quel ", "quelle ", "quels ", "quelles ", "est ce que", "peux tu m expliquer",
)


def normalize_text(value):
    value = unicodedata.normalize("NFKD", str(value or "").casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def _is_question(value):
    plain = normalize_text(value)
    return "?" in str(value or "") or any(plain.startswith(start) for start in QUESTION_STARTS)


def _has_business_topic(value):
    plain = normalize_text(value)
    return any(re.search(rf"\b{re.escape(term)}\w*\b", plain) for term in BUSINESS_TERMS)


def is_project_creation_request(value):
    plain = normalize_text(value)
    return bool(re.search(
        r"\b(creer|cree|lancer|nouveau|nouvelle|ouvrir)\b.{0,60}\bprojet\b|"
        r"\bprojet\b.{0,40}\b(creer|cree|nouveau|nouvelle)\b",
        plain,
    ))


def is_project_creation_cancel(value):
    return normalize_text(value) in {"annuler", "annule", "abandonner", "stop", "annule le projet"}


def is_project_creation_edit(value):
    plain = normalize_text(value)
    return any(re.search(rf"\b{term}\b", plain) for term in EDIT_TERMS)


def _positive_confirmation(value):
    plain = normalize_text(value)
    if not plain or _is_question(value):
        return False
    if re.search(r"\b(non|pas|jamais|refuse|annule|corriger|modifier|changer|rectifier)\b", plain):
        return False
    # Do not treat a copied instruction as confirmation.
    if plain.startswith("confirmer pour enregistrer ce projet"):
        return False
    if any(phrase in plain for phrase in ("c est quoi", "que signifie", "que veut dire")):
        return False
    words = plain.split()
    if len(words) > 10:
        return False
    if plain in {"je valide", "valider", "valide", "c est confirme", "c est bon"}:
        return True
    near_confirmation = lambda word: (
        word in {"confirmer", "confirme", "confirmee", "confirmerai"}
        or SequenceMatcher(None, word, "confirmer").ratio() >= 0.78
        or SequenceMatcher(None, word, "confirme").ratio() >= 0.78
    )
    if len(words) == 1 and near_confirmation(words[0]):
        return True
    if words[0] in {"oui", "je", "d accord", "c est"}:
        return any(near_confirmation(word) for word in words[1:5])
    if words[0] in {"confirmer", "confirme", "confirmee"} and len(words) <= 4:
        return True
    return False


def classify_assistant_intent(value, session_stage=None):
    """Route current text only; history and unrelated keywords never imply intent."""
    plain = normalize_text(value)
    if session_stage in {"COMPLETED", "completed"}:
        session_stage = None
    if is_project_creation_cancel(value) and session_stage:
        return "PROJECT_CREATION_CANCEL"
    if is_project_creation_request(value):
        return "PROJECT_CREATE"
    if session_stage and any(term in plain for term in SUMMARY_TERMS):
        return "ONG_SUMMARY"
    if session_stage and any(term in plain for term in LIST_TERMS):
        return "PROJECT_LIST"
    if session_stage in {"AWAITING_CONFIRMATION", "confirm"}:
        if _positive_confirmation(value):
            return "PROJECT_CREATION_CONFIRM"
        if is_project_creation_edit(value):
            return "PROJECT_CREATION_EDIT"
        if _is_question(value):
            if any(word.startswith("confirm") or word.startswith("comfirm") for word in plain.split()):
                return "PROJECT_CREATION_CONTINUE"
            if _has_business_topic(value):
                return "ONG_BUSINESS_QUESTION"
            return "OUT_OF_SCOPE"
        return "PROJECT_CREATION_CONTINUE"
    if session_stage:
        if is_project_creation_edit(value):
            return "PROJECT_CREATION_EDIT"
        if _is_question(value):
            if _has_business_topic(value):
                return "ONG_BUSINESS_QUESTION"
            return "OUT_OF_SCOPE"
        return "PROJECT_CREATION_CONTINUE"
    if any(term in plain for term in SUMMARY_TERMS):
        return "ONG_SUMMARY"
    if any(term in plain for term in LIST_TERMS):
        return "PROJECT_LIST"
    if _has_business_topic(value):
        return "ONG_BUSINESS_QUESTION"
    return "OUT_OF_SCOPE"
