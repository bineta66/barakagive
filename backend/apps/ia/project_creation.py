"""Deterministic, tenant-scoped conversational project creation."""
import re
import unicodedata
import hashlib
import hmac
import json

from django.db import DatabaseError, transaction
from django.db.models import Count, Q
from django.utils import timezone

from apps.accounts.models import User
from apps.ia.models import AssistantInteraction, ProjectCreationSession
from apps.projects.models import Project
from apps.projects.serializers import ProjectCreateSerializer
from apps.ia.assistant_intents import (
    classify_assistant_intent,
    is_project_creation_request as _is_project_creation_request,
    _is_question,
)


AWAITING_CONFIRMATION = "AWAITING_CONFIRMATION"
COMPLETED = "COMPLETED"
_DRAFT_FIELDS = (
    "name", "description", "region", "objectif", "start_date", "end_date",
    "chef_projet", "responsable_finance", "criteres",
)


def _plain(value):
    value = unicodedata.normalize("NFD", value.lower())
    return "".join(char for char in value if unicodedata.category(char) != "Mn")


def is_project_creation_request(text):
    return _is_project_creation_request(text)


def _dates(text):
    values = re.findall(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}-\d{2}-\d{2})\b", text)
    result = []
    for raw in values[:2]:
        try:
            if "-" in raw and raw[:4].isdigit():
                parsed = timezone.datetime.strptime(raw, "%Y-%m-%d").date()
            else:
                parsed = timezone.datetime.strptime(raw.replace("-", "/"), "%d/%m/%Y").date()
            result.append(parsed.isoformat())
        except ValueError:
            continue
    return result


def _field_values(text, data, stage=None):
    """Extract explicitly labelled facts, independent of the current dialogue step."""
    patterns = {
        "name": r"(?:nom(?: du projet)?|projet)\s*[:=]\s*([^\n;,.]{2,200})",
        "description": r"description\s*[:=]\s*([^\n;]{2,2000})",
        "objectif": r"(?:objectif|objectifs)\s*[:=]\s*([^\n;]{2,2000})",
        "region": r"(?:region|zone)\s*[:=]\s*([^\n;,.]{2,100})",
    }
    plain = _plain(text)
    for key, pattern in patterns.items():
        match = re.search(pattern, plain, re.I)
        if match:
            start, end = match.span(1)
            data[key] = text[start:end].strip()
    found_dates = _dates(text)
    normalized = _plain(text)
    start_label = re.search(r"(?:date de debut|debut)\s*[:=]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}-\d{2}-\d{2})", normalized)
    end_label = re.search(r"(?:date de fin|fin)\s*[:=]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}-\d{2}-\d{2})", normalized)
    if start_label:
        parsed = _dates(start_label.group(1))
        if parsed:
            data["start_date"] = parsed[0]
    if end_label:
        parsed = _dates(end_label.group(1))
        if parsed:
            data["end_date"] = parsed[0]
    if len(found_dates) >= 2:
        data["start_date"], data["end_date"] = found_dates[:2]
    elif found_dates and not (start_label or end_label):
        target = stage if stage in {"start_date", "end_date"} else ("start_date" if not data.get("start_date") else "end_date")
        data[target] = found_dates[0]
    return found_dates


def _is_confusion(text):
    normalized = _plain(text)
    return any(phrase in normalized for phrase in (
        "je ne comprends pas", "je comprends pas", "je n ai pas compris", "que voulez vous dire",
        "comment repondre", "je ne sais pas", "je ne suis pas sur",
    ))


def _draft_digest(data):
    draft = {key: data.get(key) for key in _DRAFT_FIELDS}
    encoded = json.dumps(draft, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _set_awaiting_confirmation(session, state, data):
    state["stage"] = AWAITING_CONFIRMATION
    state["confirmation_digest"] = _draft_digest(data)
    data["_organization_id"] = session.organization_id
    session.state = state
    session.save(update_fields=["state", "updated_at"])


def _member_options(user, role):
    members = User.objects.filter(
        organization_id=user.organization_id,
        role=role,
        status=User.Status.ACTIVE,
        is_active=True,
    ).annotate(project_load=Count(
        "projects_as_chef" if role == User.Role.CHEF_PROJET else "projects_as_finance",
        filter=Q(**{"projects_as_chef__archived": False} if role == User.Role.CHEF_PROJET else {"projects_as_finance__archived": False}),
    ))
    return list(members.order_by("project_load", "last_name", "first_name"))


def _choices(user, role, label):
    members = _member_options(user, role)
    if not members:
        return members, f"Aucun {label} actif n’est enregistré dans votre ONG. Ajoutez un membre actif, puis revenez me voir."
    options = [f"{i}. {member.full_name} ({member.project_load} projet(s))" for i, member in enumerate(members, 1)]
    return members, f"Qui sera {label} ? Répondez avec le numéro ou le nom.\n" + "\n".join(options)


def _criteria():
    return [
        {"nom": "Pertinence du besoin", "poids": 40},
        {"nom": "Niveau de vulnérabilité", "poids": 35},
        {"nom": "Faisabilité de l’accompagnement", "poids": 25},
    ]


def _next_prompt(session, text):
    state = session.state
    data = state.setdefault("data", {})
    stage = state.get("stage", "name")
    normalized = _plain(text.strip())
    if normalized in {"annuler", "annule", "abandonner", "stop"}:
        session.delete()
        return "D’accord, j’annule la création. Aucun projet n’a été créé."
    if _is_confusion(text):
        prompt = {
            "name": "Quel nom voulez-vous donner au projet ? Par exemple : « Distribution de kits scolaires ». ",
            "description": "Quelle est la description ? Par exemple : « Distribution de kits scolaires dans trois écoles ». ",
            "objectif": "Quel résultat voulez-vous atteindre ? Par exemple : « Fournir des kits à 300 élèves ». ",
            "region": "Dans quelle région le projet aura-t-il lieu ? Par exemple : « Dakar ». ",
            "start_date": "Quelle est la date de début ? Donnez le jour, le mois et l’année, par exemple 05/11/2026.",
            "end_date": "Quelle est la date de fin ? Donnez le jour, le mois et l’année, par exemple 31/12/2026.",
            "chef_projet": "Choisissez le numéro ou indiquez le nom complet d’un chef de projet actif de votre ONG.",
            "responsable_finance": "Choisissez le numéro ou indiquez le nom complet d’un responsable finance actif de votre ONG.",
            "criteria": "Je propose des critères avec des poids totalisant 100 %. Répondez « oui » pour les accepter ou donnez vos critères et leurs poids.",
            AWAITING_CONFIRMATION: "Je vous demande de confirmer l’enregistrement. Répondez « confirmer » si le récapitulatif est correct.",
            "confirm": "Je vous demande de confirmer l’enregistrement. Répondez « confirmer » si le récapitulatif est correct.",
        }.get(stage, "Dites-moi ce que vous souhaitez préciser pour le projet.")
        return f"Je reformule : {prompt}"

    if classify_assistant_intent(text, stage) == "PROJECT_CREATION_EDIT":
        correction_targets = {
            "nom": "name", "description": "description", "objectif": "objectif",
            "region": "region", "date de debut": "start_date", "date de fin": "end_date",
            "chef": "chef_projet", "finance": "responsable_finance", "critere": "criteres",
        }
        target = next((key for label, key in correction_targets.items() if label in normalized), None)
        if "budget" in normalized and target is None:
            return "Le budget n’est pas inclus dans ce brouillon. Vous pouvez corriger le nom, la description, l’objectif, la région, les dates, les responsables ou les critères. Que souhaitez-vous modifier ?"
        if target:
            state["data"].pop(target, None)
            state.pop("confirmation_digest", None)
            if target == "chef_projet":
                state["data"].pop("responsable_finance", None)
                state["data"].pop("criteres", None)
            elif target == "responsable_finance":
                state["data"].pop("criteres", None)
            state["stage"] = "criteria" if target == "criteres" else target
            session.state = state
            session.save(update_fields=["state", "updated_at"])
            prompts = {
                "name": "Quel nom voulez-vous donner au projet ?",
                "description": "Quelle description souhaitez-vous enregistrer ?",
                "objectif": "Quel est l’objectif du projet ?",
                "region": "Dans quelle région le projet sera-t-il réalisé ?",
                "start_date": "Quelle est la date de début ? (JJ/MM/AAAA)",
                "end_date": "Quelle est la date de fin ? (JJ/MM/AAAA)",
                "chef_projet": "Je vais reprendre le choix du chef de projet.",
                "responsable_finance": "Je vais reprendre le choix du responsable finance.",
                "criteres": "Je vais reprendre les critères et leurs poids.",
            }
            return prompts[target]
        return "Je ne valide pas encore. Indiquez l’élément du projet à corriger : nom, description, objectif, région, dates, chef, responsable finance ou critères."

    # A side question during a project draft is answered by the business router;
    # it must not be stored as the next field's value.
    if stage not in {COMPLETED} and classify_assistant_intent(text, stage) in {
        "ONG_BUSINESS_QUESTION", "ONG_SUMMARY", "PROJECT_LIST", "OUT_OF_SCOPE",
    }:
        return None

    dates = _field_values(text, data, stage)
    if stage == "name" and not data.get("name"):
        candidate = re.search(r"(?:creer|cree|nouveau|nouvelle)\s+(?:un\s+)?projet\s+(?:intitule\s+|nomme\s+)?(.+?)(?:\s+(?:du|decrire|objectif|region|a partir|du .* au )\b|$)", _plain(text), re.I)
        if candidate:
            data["name"] = candidate.group(1).strip().capitalize()
        elif len(text.strip()) >= 2 and normalized not in {"oui", "non"} and not is_project_creation_request(text):
            data["name"] = text.strip()[:200]
    elif stage in {"name", "description", "objectif", "region"} and not data.get(stage):
        # The current prompt gives an unambiguous meaning to a free-text answer.
        data[stage] = text.strip()[:2000]
    elif stage in {"start_date", "end_date"}:
        if dates:
            if stage == "end_date":
                data["end_date"] = dates[-1]
            else:
                data["start_date"] = dates[0]
        else:
            return "Je n’ai pas reconnu la date. Indiquez-la au format JJ/MM/AAAA."

    # Explicit labelled facts may have completed several steps in one message.
    session.state = state
    if data.get("objectif") and len(_plain(data["objectif"])) < 8:
        data.pop("objectif", None)
        state["stage"] = "objectif"
        session.state = state
        session.save(update_fields=["state", "updated_at"])
        return "L’objectif est trop court pour être compris. Décrivez le résultat attendu, par exemple : « Fournir des kits à 300 élèves »."
    for key, prompt in (
        ("name", "Quel nom voulez-vous donner au projet ?"),
        ("description", "En quelques mots, quelle est sa description ?"),
        ("objectif", "Quel changement concret le projet doit-il produire ?"),
        ("region", "Dans quelle région le projet sera-t-il réalisé ?"),
        ("start_date", "Quelle est la date de début ? (JJ/MM/AAAA)"),
        ("end_date", "Quelle est la date de fin ? (JJ/MM/AAAA)"),
    ):
        if not data.get(key):
            state["stage"] = key
            session.state = state
            session.save(update_fields=["state", "updated_at"])
            return prompt
    if data.get("start_date") and data.get("end_date") and data["end_date"] <= data["start_date"]:
        state["stage"] = "end_date"
        session.state = state
        session.save(update_fields=["state", "updated_at"])
        return "La fin doit être après le début. Quelle est la nouvelle date de fin ? (JJ/MM/AAAA)"

    if not data.get("chef_projet"):
        if stage != "chef_projet":
            state["stage"] = "chef_projet"
            members, prompt = _choices(session.user, User.Role.CHEF_PROJET, "chef de projet")
            session.save(update_fields=["state", "updated_at"])
            return prompt
        members, prompt = _choices(session.user, User.Role.CHEF_PROJET, "chef de projet")
        if not members:
            return prompt
        selected = _select_member(text, members)
        if not selected:
            return prompt
        data["chef_projet"] = selected.pk
        state["stage"] = "responsable_finance"
        session.state = state
        session.save(update_fields=["state", "updated_at"])
        _members, prompt = _choices(session.user, User.Role.FINANCE, "responsable finance")
        return f"Chef de projet retenu : {selected.full_name}.\n{prompt}"

    if not data.get("responsable_finance"):
        if stage != "responsable_finance":
            state["stage"] = "responsable_finance"
            _members, prompt = _choices(session.user, User.Role.FINANCE, "responsable finance")
            session.save(update_fields=["state", "updated_at"])
            return prompt
        members, prompt = _choices(session.user, User.Role.FINANCE, "responsable finance")
        if not members:
            return prompt
        selected = _select_member(text, members)
        if not selected:
            return prompt
        data["responsable_finance"] = selected.pk
        state["stage"] = "criteria"
        session.state = state
        session.save(update_fields=["state", "updated_at"])
        return f"Responsable finance retenu : {selected.full_name}.\nJe propose trois critères : Pertinence du besoin (40 %), Vulnérabilité (35 %), Faisabilité (25 %). Répondez « oui » ou indiquez vos critères et poids, pour un total de 100 %."

    if not data.get("criteres"):
        if stage != "criteria":
            state["stage"] = "criteria"
            session.save(update_fields=["state", "updated_at"])
            return "Je propose trois criteres : Pertinence du besoin (40 %), Vulnerabilite (35 %), Faisabilite (25 %). Repondez oui pour les accepter ou indiquez des criteres dont les poids totalisent 100 %."
        if normalized not in {"oui", "oui ca me va", "accepter", "accepte", "valider", "d accord", "ok"}:
            weights = [int(value) for value in re.findall(r"\b\d{1,3}\b", text)]
            if len(weights) == 3 and sum(weights) == 100 and all(1 <= value <= 100 for value in weights):
                data["criteres"] = _criteria()
                for criterion, weight in zip(data["criteres"], weights):
                    criterion["poids"] = weight
            elif "critere" in normalized and ":" in text:
                pairs = re.findall(r"([^,;:]+?)\s*[:=]\s*(\d{1,3})\s*%?", text)
                criteria = [{"nom": name.strip()[:200], "poids": int(weight)} for name, weight in pairs]
                if not criteria or sum(item["poids"] for item in criteria) != 100 or any(item["poids"] < 1 for item in criteria):
                    return "Les poids doivent totaliser exactement 100 %. Vous pouvez accepter ma proposition, donner trois poids ou ecrire vos criteres sous la forme Nom : poids."
                data["criteres"] = criteria
            else:
                return "Les criteres proposes sont : Pertinence du besoin (40 %), Vulnerabilite (35 %), Faisabilite (25 %). Repondez oui, donnez trois poids totalisant 100 ou precisez vos criteres sous la forme Nom : poids."
        else:
            data["criteres"] = _criteria()
        _set_awaiting_confirmation(session, state, data)
        return _summary(data) + "\n\nRepondez confirmer pour enregistrer ce projet, ou indiquez une correction."

    if data.get("criteres") and stage not in {AWAITING_CONFIRMATION, "confirm"}:
        _set_awaiting_confirmation(session, state, data)
        return _summary(data) + "\n\nRepondez confirmer pour enregistrer ce projet, ou indiquez une correction."

    if stage in {AWAITING_CONFIRMATION, "confirm"}:
        intent = classify_assistant_intent(text, AWAITING_CONFIRMATION)
        if intent != "PROJECT_CREATION_CONFIRM":
            if normalized in {"non", "non merci", "pas encore", "je ne confirme pas", "je confirme pas"}:
                return "D'accord, je n'enregistre pas le projet. Le brouillon reste disponible. Dites-moi si vous souhaitez le corriger ou l'annuler."
            if _is_question(text):
                return "Je n'ai pas compris si vous souhaitez enregistrer le projet. Repondez confirmer pour l'enregistrer, ou dites-moi ce que vous souhaitez corriger. Le brouillon est conserve."
            return "Le brouillon est conserve. Repondez confirmer pour enregistrer ce projet, ou indiquez l'element a corriger."
        return None


def _select_member(text, members):
    normalized = _plain(text)
    numbers = re.findall(r"\b\d+\b", normalized)
    if numbers and 1 <= int(numbers[0]) <= len(members):
        return members[int(numbers[0]) - 1]
    return next((member for member in members if _plain(member.full_name) in normalized), None)


def _summary(data):
    start = data.get("start_date", "")
    end = data.get("end_date", "")
    chef = User.objects.filter(pk=data.get("chef_projet"), organization_id=data.get("_organization_id")).first()
    finance = User.objects.filter(pk=data.get("responsable_finance"), organization_id=data.get("_organization_id")).first()
    criteria = data.get("criteres", _criteria())
    criteria_text = ", ".join(f"{item['nom']} ({item['poids']} %)" for item in criteria)
    return (
        f"Récapitulatif : {data.get('name', 'Projet sans nom')} dans {data.get('region', 'région à préciser')}. "
        f"{data.get('description', '')} Objectif : {data.get('objectif', '')} "
        f"Du {start} au {end}. Chef de projet : {chef.full_name if chef else 'à choisir'}. "
        f"Responsable finance : {finance.full_name if finance else 'à choisir'}. "
        f"Critères : {criteria_text}. Total : {sum(item['poids'] for item in criteria)} %."
    )


@transaction.atomic
def handle_project_creation(user, conversation_id, text, request):
    if user.role != User.Role.GERANT or not user.organization_id:
        return None
    session = ProjectCreationSession.objects.select_for_update().filter(
        conversation_id=conversation_id, user=user,
    ).first()
    if session and session.organization_id != user.organization_id:
        return "Cette conversation appartient a une autre organisation. Commencez une nouvelle conversation."

    if session and session.project_id:
        repeated_confirmation = classify_assistant_intent(text, AWAITING_CONFIRMATION) == "PROJECT_CREATION_CONFIRM"
        if repeated_confirmation:
            return f"Le projet {session.project.name} est deja enregistre sous le code {session.project.code}."
        if is_project_creation_request(text):
            session.project = None
            session.state = {"stage": "name", "data": {}}
            session.save(update_fields=["project", "state", "updated_at"])
        else:
            return None

    if session is None:
        if not is_project_creation_request(text):
            return None
        session, _created = ProjectCreationSession.objects.get_or_create(
            conversation_id=conversation_id,
            user=user,
            defaults={
                "organization_id": user.organization_id,
                "state": {"stage": "name", "data": {}},
            },
        )

    session.state.setdefault("data", {})["_organization_id"] = session.organization_id
    current_stage = session.state.get("stage")
    current_intent = classify_assistant_intent(text, current_stage)
    if current_stage not in {COMPLETED} and current_intent in {
        "ONG_BUSINESS_QUESTION", "ONG_SUMMARY", "PROJECT_LIST", "OUT_OF_SCOPE",
    }:
        return None

    response = _next_prompt(session, text)
    if response is not None:
        AssistantInteraction.objects.create(
            conversation_id=conversation_id, user=user, organization_id=user.organization_id,
            request_text=text[:4000], response_text=response[:12000],
            tools_used=["project_creation_conversation"],
        )
        return response

    state = session.state
    data = state["data"]
    if state.get("stage") not in {AWAITING_CONFIRMATION, "confirm"}:
        return "Le brouillon est conserve. Veuillez confirmer le recapitulatif avant l'enregistrement."
    if classify_assistant_intent(text, AWAITING_CONFIRMATION) != "PROJECT_CREATION_CONFIRM":
        return "Le brouillon est conserve. Dites-moi si vous souhaitez confirmer ou corriger une information."

    expected_digest = state.get("confirmation_digest")
    if not expected_digest or not hmac.compare_digest(expected_digest, _draft_digest(data)):
        _set_awaiting_confirmation(session, state, data)
        return _summary(data) + "\n\nLe brouillon a change. Verifiez ce recapitulatif, puis repondez confirmer."

    payload = {key: data[key] for key in _DRAFT_FIELDS}
    serializer = ProjectCreateSerializer(data=payload, context={"request": request})
    if not serializer.is_valid():
        details = []
        for field, errors in serializer.errors.items():
            if isinstance(errors, (list, tuple)):
                details.append(f"{field}: {', '.join(str(error) for error in errors)}")
            else:
                details.append(f"{field}: {errors}")
        message = "Le projet n'a pas ete enregistre. " + "; ".join(details) + ". Le brouillon est conserve."
        AssistantInteraction.objects.create(
            conversation_id=conversation_id, user=user, organization_id=user.organization_id,
            request_text=text[:4000], response_text=message[:12000],
            tools_used=["project_creation_validation_error"],
        )
        return message

    try:
        with transaction.atomic():
            project = serializer.save()
            project = Project.objects.get(pk=project.pk, organization_id=user.organization_id)
    except (DatabaseError, Project.DoesNotExist):
        message = "Django n'a pas pu enregistrer le projet. Le brouillon est conserve ; verifiez les informations puis reessayez."
        AssistantInteraction.objects.create(
            conversation_id=conversation_id, user=user, organization_id=user.organization_id,
            request_text=text[:4000], response_text=message,
            tools_used=["project_creation_database_error"],
        )
        return message

    state["stage"] = COMPLETED
    state["completed_project_id"] = project.pk
    state["completed_project_code"] = project.code
    session.project = project
    session.state = state
    session.save(update_fields=["project", "state", "updated_at"])
    message = f"Votre projet {project.name} a ete cree avec succes (code {project.code}). Vous pouvez consulter sa fiche ou demarrer la creation d'un autre projet."
    AssistantInteraction.objects.create(
        conversation_id=conversation_id, user=user, organization_id=user.organization_id,
        request_text=text[:4000], response_text=message, tools_used=["create_project"],
    )
    return message
