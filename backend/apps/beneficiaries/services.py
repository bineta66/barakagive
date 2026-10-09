import logging
import uuid
from datetime import date

from django.db import transaction

logger = logging.getLogger(__name__)

from .models import FormResponse


def _validate_form_response_links(beneficiary, formulaire, question):
    campaign = formulaire.campagne
    if (
        beneficiary.organization_id != formulaire.organization_id
        or beneficiary.campagne_id != formulaire.campagne_id
        or question.formulaire_id != formulaire.pk
        or campaign.organization_id != formulaire.organization_id
        or campaign.projet.organization_id != formulaire.organization_id
    ):
        raise BeneficiaryError(
            "Le bénéficiaire, le formulaire, la campagne et le projet doivent appartenir à la même ONG."
        )
    if question.critere_id and question.critere.projet_id != campaign.projet_id:
        raise BeneficiaryError("La question est liée à un critère d'un autre projet.")
    reverse_criteria = list(question.criteria.all())
    if any(item.projet_id != campaign.projet_id for item in reverse_criteria):
        raise BeneficiaryError("La question est liée à un critère d'un autre projet.")
    if question.critere_id and any(item.pk != question.critere_id for item in reverse_criteria):
        raise BeneficiaryError("Les liens question/critère sont contradictoires.")


@transaction.atomic
def enregistrer_reponse(
    *,
    beneficiary,
    formulaire_id,
    question_id,
    value_boolean=None,
    value_text=None,
    value_number=None,
    value_date=None,
    value_json=None,
):
    """
    Crée ou met à jour la réponse d'un bénéficiaire.
    Le calcul du score sera déclenché après l'enregistrement.
    """
    from apps.forms.models import Formulaire, FormField

    try:
        formulaire = Formulaire.objects.select_related("campagne__projet").get(pk=formulaire_id)
        question = FormField.objects.select_related("formulaire", "critere").get(pk=question_id)
    except (Formulaire.DoesNotExist, FormField.DoesNotExist):
        raise BeneficiaryError("Le formulaire ou la question n'existe pas.")
    _validate_form_response_links(beneficiary, formulaire, question)

    reponse, _ = FormResponse.objects.update_or_create(
        beneficiary=beneficiary,
        question_id=question_id,
        defaults={
            "formulaire_id": formulaire_id,
            "value_boolean": value_boolean,
            "value_text": value_text,
            "value_number": value_number,
            "value_date": value_date,
            "value_json": value_json,
        },
    )

    return reponse


from decimal import Decimal, InvalidOperation
from django.db import transaction


YES_VALUES = {
    "oui",
    "yes",
    "true",
    "1",
    "vrai",
    "on",
}


def _normaliser_valeur(reponse):
    """
    Retourne la valeur d'une réponse sous forme de texte comparable.
    """
    if reponse.value_boolean is not None:
        return "true" if reponse.value_boolean else "false"

    if reponse.value_text is not None:
        return reponse.value_text.strip().lower()

    if reponse.value_number is not None:
        return str(reponse.value_number).strip().lower()

    if reponse.value_json is not None:
        return str(reponse.value_json).strip().lower()

    return ""


def _reponse_est_vulnerable(reponse, critere):
    valeur = _normaliser_valeur(reponse)
    valeurs_vulnerables = {
        str(item).strip().lower()
        for item in (critere.vulnerable_values or [])
    }

    if valeurs_vulnerables:
        if critere.vulnerable_operator in {"equals", "in", "contains"}:
            return valeur in valeurs_vulnerables

    return valeur in YES_VALUES


def _get_project_from_campaign(campagne):
    """
    Adapte automatiquement le nom de la relation Campaign -> Project.
    Le projet peut être exposé sous 'projet' ou 'project'.
    """
    if hasattr(campagne, "projet") and campagne.projet:
        return campagne.projet

    if hasattr(campagne, "project") and campagne.project:
        return campagne.project

    if hasattr(campagne, "projet_id") and campagne.projet_id:
        return campagne.projet

    if hasattr(campagne, "project_id") and campagne.project_id:
        return campagne.project

    raise AttributeError(
        "Campaign doit avoir une relation 'projet' ou 'project' vers Project."
    )


@transaction.atomic
def recalculer_score_beneficiaire(beneficiary):
    """
    Calcule et enregistre le score de vulnérabilité d'un bénéficiaire.
    """
    return update_vulnerability_score(beneficiary).score_vulnerabilite


from django.db import transaction
from decimal import Decimal

from apps.campaigns.models import Campaign, CampagneAffectation
from apps.zones.models import Zone
from apps.zones.models import Region
from apps.forms.models import Formulaire, FormField
from .models import Beneficiary, FormResponse


class BeneficiaryError(Exception):
    """Exception personnalisée pour les erreurs de bénéficiaire."""
    pass


def build_zone_ranking(campaign, user=None):
    """
    Construit le classement des zones pour une campagne.

    Args:
        campaign: Instance de Campaign

    Returns:
        list[dict]: Classement des zones avec score_total, beneficiaires_prioritaires, top5
    """
    beneficiaries = Beneficiary.objects.filter(
        campagne=campaign,
        organization_id=campaign.organization_id,
        campagne__organization_id=campaign.organization_id,
        campagne__projet__organization_id=campaign.organization_id,
        zone__organization_id=campaign.organization_id,
    ).select_related("zone").prefetch_related("responses__question").order_by("-score_vulnerabilite")
    if user and user.role == "AGENT":
        assigned_zone_names = CampagneAffectation.objects.filter(
            campagne=campaign,
            agent=user,
        ).values_list("zone", flat=True)
        beneficiaries = beneficiaries.filter(zone__nom__in=assigned_zone_names)

    zones_data = {}
    for beneficiary in beneficiaries:
        zone_nom = beneficiary.zone.nom if beneficiary.zone else "Inconnue"
        if zone_nom not in zones_data:
            zones_data[zone_nom] = {
                "nom": zone_nom,
                "score_total": Decimal("0"),
                "beneficiaires": [],
            }
        score = beneficiary.score_vulnerabilite or Decimal("0")
        zones_data[zone_nom]["score_total"] += score
        zones_data[zone_nom]["beneficiaires"].append({
            "id": str(beneficiary.id),
            "nom": f"{beneficiary.prenom} {beneficiary.nom}",
            "score": int(score),
            "raisons": _extraire_raisons(beneficiary),
        })

    classement = []
    for zone_nom, data in zones_data.items():
        beneficiaires_tries = sorted(
            data["beneficiaires"],
            key=lambda b: b["score"],
            reverse=True,
        )
        top5 = beneficiaires_tries[:5]
        classement.append({
            "nom": data["nom"],
            "score_total": int(data["score_total"]),
            "beneficiaires_prioritaires": len([b for b in data["beneficiaires"] if b["score"] >= 70]),
            "top5": top5,
        })

    classement.sort(key=lambda z: z["score_total"], reverse=True)
    return classement


def _extraire_raisons(beneficiary):
    """
    Extrait les raisons de priorisation d'un bénéficiaire à partir de ses réponses.
    """
    raisons = []
    try:
        responses = beneficiary.responses.select_related("question").all()
        for response in responses:
            valeur = _extraire_valeur_reponse(response)
            if _est_reponse_vulnerable(valeur):
                label = response.question.label
                valeur_lisible = _formatter_valeur(response, valeur)
                if valeur_lisible:
                    raisons.append(f"{label} : {valeur_lisible}")
                else:
                    raisons.append(label)
    except Exception:
        pass
    return raisons[:3]


def _formatter_valeur(response, valeur):
    """
    Formate la valeur d'une réponse pour l'afficher dans les raisons.
    """
    if valeur is None:
        return None

    if isinstance(valeur, bool):
        return "Oui" if valeur else "Non"

    if isinstance(valeur, (int, float)):
        return str(valeur)

    if isinstance(valeur, str):
        texte = valeur.strip()
        return texte or None

    if isinstance(valeur, list):
        if not valeur:
            return None
        return ", ".join(str(v) for v in valeur)

    if isinstance(valeur, dict):
        return str(valeur)

    return str(valeur)


def validate_agent_permissions(user, campaign, zone, formulaire):
    """
    Vérifie que l'agent a les droits pour créer un bénéficiaire.

    Args:
        user: Utilisateur connecté (AGENT)
        campaign: Instance de Campaign
        zone: Instance de Zone
        formulaire: Instance de Formulaire

    Raises:
        BeneficiaryError: Si une vérification échoue
    """
    if not user.organization:
        raise BeneficiaryError("Vous n'appartenez à aucune ONG.")

    if campaign.organization != user.organization:
        raise BeneficiaryError("La campagne n'appartient pas à votre ONG.")

    if campaign.projet.organization_id != campaign.organization_id:
        raise BeneficiaryError("Le projet de la campagne n'appartient pas à son ONG.")

    if campaign.projet.organization_id != user.organization_id:
        raise BeneficiaryError("Le projet de la campagne n'appartient pas à votre ONG.")

    if zone.organization != user.organization:
        raise BeneficiaryError("La zone n'appartient pas à votre ONG.")

    if zone not in campaign.zones.all():
        raise BeneficiaryError("La zone ne fait pas partie de cette campagne.")

    if formulaire is None:
        raise BeneficiaryError("Un formulaire publié est requis pour cette campagne.")

    if user.role == "AGENT":
        assigned_zones = list(
            CampagneAffectation.objects.filter(
                campagne=campaign,
                agent=user,
            ).values_list("zone", flat=True)
        )
        if zone.nom not in set(assigned_zones) and str(zone.id) not in set(assigned_zones):
            raise BeneficiaryError("La zone ne correspond pas à votre affectation.")

    if formulaire.campagne != campaign:
        raise BeneficiaryError("Le formulaire n'appartient pas à cette campagne.")

    if formulaire.organization_id != campaign.organization_id:
        raise BeneficiaryError("Le formulaire et sa campagne doivent appartenir à la même ONG.")

    if formulaire.statut != Formulaire.Statut.PUBLIE:
        raise BeneficiaryError("Le formulaire doit être publié pour être utilisé.")


def check_duplicate_in_campaign(campaign, telephone, nom, prenom, date_naissance, exclude_id=None, zone=None):
    """
    Vérifie si un bénéficiaire existe déjà dans la campagne.

    Règle : téléphone en priorité, sinon nom + prénom + date_naissance.

    Args:
        campaign: Instance de Campaign
        telephone: Téléphone du bénéficiaire
        nom: Nom
        prenom: Prénom
        date_naissance: Date de naissance
        exclude_id: ID à exclure (pour mise à jour)

    Returns:
        Beneficiary or None: Le doublon trouvé ou None
    """
    queryset = Beneficiary.objects.filter(
        campagne=campaign,
        organization_id=campaign.organization_id,
        campagne__projet__organization_id=campaign.organization_id,
        zone__organization_id=campaign.organization_id,
    )
    if zone is not None:
        queryset = queryset.filter(zone=zone)

    if exclude_id:
        queryset = queryset.exclude(id=exclude_id)

    # Priorité 1 : téléphone
    duplicate = queryset.filter(telephone=telephone).first()
    if duplicate:
        return duplicate

    # Priorité 2 : nom + prénom + date_naissance
    duplicate = queryset.filter(
        nom__iexact=nom,
        prenom__iexact=prenom,
        date_naissance=date_naissance,
    ).first()

    return duplicate


def check_sync_duplicate(local_id, device_id, organization_id):
    """
    Vérifie si un bénéficiaire avec ce local_id + device_id existe déjà
    (pour éviter les doublons de synchronisation hors ligne).

    Args:
        local_id: UUID local
        device_id: ID du dispositif

    Returns:
        Beneficiary or None
    """
    return Beneficiary.objects.filter(
        local_id=local_id,
        device_id=device_id,
        organization_id=organization_id,
        campagne__organization_id=organization_id,
        campagne__projet__organization_id=organization_id,
        zone__organization_id=organization_id,
        created_by__organization_id=organization_id,
    ).first()


def store_response(beneficiary, formulaire, question, value):
    """
    Stocke une réponse selon le type de question.

    Args:
        beneficiary: Instance de Beneficiary
        formulaire: Instance de Formulaire
        question: Instance de FormField
        value: Valeur brute (JSON)

    Returns:
        FormResponse: La réponse créée
    """
    _validate_form_response_links(beneficiary, formulaire, question)

    response_data = {
        "beneficiary": beneficiary,
        "formulaire": formulaire,
        "question": question,
    }

    field_type = question.type

    validate_dynamic_response_value(question, value)

    if field_type in [
        FormField.TypeChoices.TEXT, FormField.TypeChoices.PHONE, FormField.TypeChoices.TEXTAREA,
        FormField.TypeChoices.EMAIL, FormField.TypeChoices.RADIO,
        FormField.TypeChoices.PHOTO, FormField.TypeChoices.FILE,
    ]:
        response_data["value_text"] = str(value) if value is not None else ""

    elif field_type == FormField.TypeChoices.SELECT:
        response_data["value_text"] = str(value) if value is not None else ""

    elif field_type == FormField.TypeChoices.CHECKBOX:
        if isinstance(value, list):
            response_data["value_json"] = value
        else:
            response_data["value_json"] = [value] if value else []

    elif field_type == FormField.TypeChoices.YES_NO:
        if isinstance(value, bool):
            response_data["value_boolean"] = value
        elif isinstance(value, str):
            response_data["value_boolean"] = value.strip().lower() in ["true", "oui", "yes", "1"]
        else:
            response_data["value_boolean"] = bool(value)

    elif field_type == FormField.TypeChoices.NUMBER:
        response_data["value_number"] = Decimal(str(value)) if value not in (None, "") else None

    elif field_type == FormField.TypeChoices.SCALE:
        response_data["value_number"] = Decimal(str(value)) if value not in (None, "") else None

    elif field_type == FormField.TypeChoices.DATE:
        response_data["value_date"] = date.fromisoformat(str(value)) if value not in (None, "") else None

    elif field_type == FormField.TypeChoices.GPS:
        response_data["value_json"] = {
            "latitude": str(value["latitude"]) if value.get("latitude") not in (None, "") else None,
            "longitude": str(value["longitude"]) if value.get("longitude") not in (None, "") else None,
        }

    return FormResponse.objects.create(**response_data)


def validate_dynamic_response_value(question, value):
    """Reject malformed answers before they are persisted."""
    import re
    from datetime import date

    field_type = question.type
    empty = value is None or value == "" or value == []
    if field_type == FormField.TypeChoices.GPS and isinstance(value, dict):
        empty = not str(value.get("latitude", "")).strip() and not str(value.get("longitude", "")).strip()
    if empty:
        if question.obligatoire:
            raise BeneficiaryError(f"La r?ponse ? ? {question.label} ? est obligatoire.")
        return

    if field_type in (FormField.TypeChoices.TEXT, FormField.TypeChoices.TEXTAREA):
        if not isinstance(value, str):
            raise BeneficiaryError(f"La r?ponse ? ? {question.label} ? doit ?tre du texte.")
    elif field_type == FormField.TypeChoices.EMAIL:
        from apps.common.validators import validate_email
        if not isinstance(value, str):
            raise BeneficiaryError(f"La r?ponse ? ? {question.label} ? doit ?tre une adresse email.")
        try:
            validate_email(value)
        except Exception as exc:
            raise BeneficiaryError(f"{question.label} : {exc}") from exc
    elif field_type == FormField.TypeChoices.PHONE:
        from apps.common.validators import validate_phone_senegal
        if not isinstance(value, str):
            raise BeneficiaryError(f"La r?ponse ? ? {question.label} ? doit ?tre un num?ro de t?l?phone.")
        try:
            validate_phone_senegal(value)
        except Exception as exc:
            raise BeneficiaryError(f"{question.label} : {exc}") from exc
    elif field_type == FormField.TypeChoices.NUMBER:
        if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
            raise BeneficiaryError(f"La réponse pour « {question.label} » doit être un nombre valide.")
        try:
            number = Decimal(str(value))
            if not number.is_finite():
                raise InvalidOperation
        except (InvalidOperation, ValueError, TypeError):
            raise BeneficiaryError(f"La réponse pour « {question.label} » doit être un nombre valide.")
    elif field_type == FormField.TypeChoices.DATE:
        if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise BeneficiaryError(f"La r?ponse ? ? {question.label} ? doit ?tre une date au format AAAA-MM-JJ.")
        try:
            date.fromisoformat(value)
        except ValueError:
            raise BeneficiaryError(f"La r?ponse ? ? {question.label} ? doit ?tre une date valide.")
    elif field_type in (FormField.TypeChoices.SELECT, FormField.TypeChoices.RADIO):
        options = question.options if isinstance(question.options, list) else []
        if value not in options:
            raise BeneficiaryError(f"Veuillez choisir une option valide pour ? {question.label} ?.")
    elif field_type == FormField.TypeChoices.CHECKBOX:
        options = question.options if isinstance(question.options, list) else []
        if not isinstance(value, list) or any(option not in options for option in value):
            raise BeneficiaryError(f"Les choix de ? {question.label} ? sont invalides.")
    elif field_type == FormField.TypeChoices.YES_NO:
        if not isinstance(value, bool):
            raise BeneficiaryError(f"La r?ponse ? ? {question.label} ? doit ?tre un bool?en.")
    elif field_type == FormField.TypeChoices.SCALE:
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 5:
            raise BeneficiaryError(f"La r?ponse ? ? {question.label} ? doit ?tre un entier compris entre 1 et 5.")
    elif field_type in (FormField.TypeChoices.PHOTO, FormField.TypeChoices.FILE):
        if not isinstance(value, str) or len(value) > 255 or any(ord(char) < 32 for char in value):
            raise BeneficiaryError(f"La r?ponse ? ? {question.label} ? doit ?tre un nom de fichier valide.")
    elif field_type == FormField.TypeChoices.GPS:
        if not isinstance(value, dict) or set(value) - {"latitude", "longitude"}:
            raise BeneficiaryError(f"La r?ponse ? ? {question.label} ? doit contenir uniquement des coordonn?es GPS.")
        try:
            if isinstance(value["latitude"], bool) or isinstance(value["longitude"], bool):
                raise InvalidOperation
            latitude = Decimal(str(value["latitude"]))
            longitude = Decimal(str(value["longitude"]))
            if not latitude.is_finite() or not longitude.is_finite() or not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
                raise InvalidOperation
        except (KeyError, InvalidOperation, ValueError, TypeError):
            raise BeneficiaryError(f"Les coordonn?es de ? {question.label} ? sont invalides.")


def validate_form_responses(formulaire, responses):
    """Ensure submitted answers belong to the selected form and required fields are answered."""
    campaign = formulaire.campagne
    if (
        formulaire.organization_id != campaign.organization_id
        or campaign.projet.organization_id != campaign.organization_id
    ):
        raise BeneficiaryError("Le formulaire, la campagne et le projet doivent appartenir à la même ONG.")

    questions = {
        str(question.id): question
        for question in formulaire.fields.select_related("critere", "formulaire").all()
    }
    submitted = {str(item["question_id"]): item.get("value") for item in responses}

    unknown_ids = set(submitted) - set(questions)
    if unknown_ids:
        raise BeneficiaryError("Une réponse référence une question qui ne fait pas partie de ce formulaire.")

    for question_id, question in questions.items():
        if question.critere_id:
            if question.critere.projet_id != campaign.projet_id:
                raise BeneficiaryError("Une question du formulaire est liée à un critère d'un autre projet.")
        reverse_criteria = list(question.criteria.all())
        if any(item.projet_id != campaign.projet_id for item in reverse_criteria):
            raise BeneficiaryError("Une question du formulaire est liée à un critère d'un autre projet.")
        if question.critere_id and any(item.pk != question.critere_id for item in reverse_criteria):
            raise BeneficiaryError("Les liens question/critère du formulaire sont contradictoires.")
        validate_dynamic_response_value(question, submitted.get(question_id))


def create_beneficiary_with_responses(validated_data, user):
    """
    Crée un bénéficiaire et ses réponses en une seule transaction.
    Gère la détection de doublons et la séparation automatique des données.

    Args:
        validated_data: Données validées du serializer
        user: Utilisateur connecté (AGENT)

    Returns:
        tuple: (beneficiary, responses, is_duplicate)

    Raises:
        BeneficiaryError: Si une validation échoue
    """
    # Views validate first, but services can also be called by other internal
    # entry points. Revalidate here so no direct caller can bypass payload
    # shape, type, format, or field allow-list checks.
    from .serializers import BeneficiaryCreateSerializer

    serializer = BeneficiaryCreateSerializer(data=validated_data)
    if not serializer.is_valid():
        raise BeneficiaryError(
            "Données de bénéficiaire invalides : "
            + "; ".join(
                f"{field}: {', '.join(str(error) for error in errors)}"
                for field, errors in serializer.errors.items()
            )
        )
    validated_data = serializer.validated_data

    campagne_id = validated_data["campagne_id"]
    formulaire_id = validated_data.get("formulaire_id")
    zone_id = validated_data["zone_id"]
    local_id = validated_data.get("local_id") or uuid.uuid4()
    device_id = validated_data.get("device_id") or "web"
    beneficiary_data = validated_data["beneficiary"]
    responses_data = validated_data.get("responses") or []

    # Récupérer les objets
    try:
        campaign = Campaign.objects.select_related("projet", "organization").get(id=campagne_id)
    except Campaign.DoesNotExist:
        raise BeneficiaryError("La campagne spécifiée n'existe pas.")

    try:
        zone = Zone.objects.get(id=zone_id)
    except Zone.DoesNotExist:
        raise BeneficiaryError("La zone spécifiée n'existe pas.")

    formulaire = None
    if formulaire_id:
        try:
            formulaire = Formulaire.objects.select_related("campagne", "organization").get(id=formulaire_id)
        except Formulaire.DoesNotExist:
            formulaire = None

    # Vérifications de permissions
    validate_agent_permissions(user, campaign, zone, formulaire)
    validate_form_responses(formulaire, responses_data)

    # Vérifier doublon de synchronisation (local_id + device_id)
    if local_id and device_id != "web":
        sync_duplicate = check_sync_duplicate(local_id, device_id, user.organization_id)
        if sync_duplicate:
            raise BeneficiaryError("Ce bénéficiaire a déjà été synchronisé depuis ce dispositif.")

    # Extraire les données personnelles
    telephone = str(beneficiary_data["telephone"]).strip()
    nom = str(beneficiary_data["nom"]).strip()
    prenom = str(beneficiary_data["prenom"]).strip()
    date_naissance = str(beneficiary_data["date_naissance"]).strip()

    # Vérifier doublon dans la campagne
    duplicate = check_duplicate_in_campaign(
        campaign, telephone, nom, prenom, date_naissance
    )
    if duplicate:
        zone_info = f" (Zone : {duplicate.zone.nom})" if duplicate.zone else ""
        if duplicate.telephone == telephone:
            raise BeneficiaryError(
                f"Ce numéro de téléphone ({telephone}) est déjà enregistré dans cette campagne{zone_info}."
            )
        else:
            raise BeneficiaryError(
                f"Le bénéficiaire {nom} {prenom} (né(e) le {date_naissance}) est déjà enregistré dans cette campagne{zone_info}."
            )

    # Repli automatique sur les coordonnées de la zone ou région si non fournies
    lat_val = beneficiary_data.get("latitude")
    lng_val = beneficiary_data.get("longitude")

    if not lat_val or str(lat_val).strip() in ("", "None", "0"):
        lat_val = str(zone.latitude) if zone and zone.latitude else None
    if not lng_val or str(lng_val).strip() in ("", "None", "0"):
        lng_val = str(zone.longitude) if zone and zone.longitude else None
    if lat_val is None or lng_val is None:
        raise BeneficiaryError("La position GPS est indisponible et cette zone ne possède pas de coordonnées enregistrées.")

    # Créer le bénéficiaire et les réponses
    with transaction.atomic():
        beneficiary = Beneficiary.objects.create(
            campagne=campaign,
            zone=zone,
            organization=campaign.organization,
            nom=nom,
            prenom=prenom,
            telephone=telephone,
            sexe=beneficiary_data["sexe"],
            date_naissance=date_naissance,
            latitude=str(lat_val),
            longitude=str(lng_val),
            local_id=local_id,
            device_id=device_id,
            created_by=user,
            sync_status=Beneficiary.SyncStatus.SYNCED,
        )

        created_responses = []
        if formulaire:
            # Récupérer toutes les questions du formulaire
            questions = {str(q.id): q for q in formulaire.fields.all()}

            # Créer les réponses
            for resp_data in responses_data:
                question_id = str(resp_data.get("question_id"))
                value = resp_data.get("value")

                if question_id in questions:
                    question = questions[question_id]
                    if resp_data.get("value") is None or resp_data.get("value") == "" or resp_data.get("value") == []:
                        continue
                    response = store_response(beneficiary, formulaire, question, value)
                    created_responses.append(response)

        beneficiary = update_vulnerability_score(beneficiary)

    return beneficiary, created_responses, False


def update_beneficiary(beneficiary, validated_data, user):
    """
    Met à jour les informations personnelles d'un bénéficiaire.

    Args:
        beneficiary: Instance de Beneficiary
        validated_data: Données validées
        user: Utilisateur connecté

    Returns:
        Beneficiary: Le bénéficiaire mis à jour
    """
    # Vérifier les permissions
    if user.role == "AGENT" and beneficiary.created_by != user:
        raise BeneficiaryError("Vous ne pouvez modifier que vos propres bénéficiaires.")

    if beneficiary.organization != user.organization:
        raise BeneficiaryError("Ce bénéficiaire n'appartient pas à votre ONG.")

    # Vérifier doublon si téléphone changé
    if "telephone" in validated_data and validated_data["telephone"] != beneficiary.telephone:
        duplicate = check_duplicate_in_campaign(
            beneficiary.campagne,
            validated_data["telephone"],
            validated_data.get("nom", beneficiary.nom),
            validated_data.get("prenom", beneficiary.prenom),
            validated_data.get("date_naissance", beneficiary.date_naissance),
            exclude_id=beneficiary.id,
        )
        if duplicate:
            raise BeneficiaryError("Un autre bénéficiaire avec ce téléphone existe déjà dans cette campagne.")

    for field, value in validated_data.items():
        setattr(beneficiary, field, value)

    beneficiary.save()
    return beneficiary


def sync_pending_beneficiaries(pending_data_list, user):
    """
    Synchronise une liste de bénéficiaires en attente (mode hors ligne).
    Chaque bénéficiaire est traité dans sa propre transaction.

    Args:
        pending_data_list: Liste de données de bénéficiaires
        user: Utilisateur connecté (AGENT)

    Returns:
        dict: Résultat de la synchronisation {synced, duplicates, failed, details}
    """
    results = {
        "synced": 0,
        "duplicates": 0,
        "failed": 0,
        "details": [],
    }

    for data in pending_data_list:
        try:
            with transaction.atomic():
                beneficiary, responses, is_duplicate = create_beneficiary_with_responses(data, user)

            if is_duplicate:
                results["duplicates"] += 1
                results["details"].append({
                    "local_id": str(beneficiary.local_id),
                    "status": "DUPLICATE",
                    "beneficiary_id": str(beneficiary.id),
                })
            else:
                results["synced"] += 1
                results["details"].append({
                    "local_id": str(beneficiary.local_id),
                    "status": "SYNCED",
                    "beneficiary_id": str(beneficiary.id),
                })

        except BeneficiaryError as e:
            results["failed"] += 1
            results["details"].append({
                "local_id": str(data.get("local_id", "unknown")),
                "status": "FAILED",
                "error": str(e),
            })
        except Exception as e:
            results["failed"] += 1
            results["details"].append({
                "local_id": str(data.get("local_id", "unknown")),
                "status": "FAILED",
                "error": f"Erreur inattendue : {str(e)}",
            })

    return results


def _find_response_for_criterion(criterion, responses_by_qid, responses_by_label, all_responses, index=None):
    """
    Associe un critère de projet à la réponse correspondante du bénéficiaire :
    1. Par question_id (si relié explicitement)
    2. Par correspondance du libellé de la question et du nom du critère (insensible à la casse/accents)
    3. Par inclusion de texte (sous-chaîne)
    4. Par ordre d'index si les nombres d'éléments coïncident
    """
    if criterion.question_id and str(criterion.question_id) in responses_by_qid:
        return responses_by_qid[str(criterion.question_id)]

    crit_norm = normalize_region_name(criterion.nom)
    if crit_norm and crit_norm in responses_by_label:
        return responses_by_label[crit_norm]

    if crit_norm:
        for lbl_norm, resp in responses_by_label.items():
            if crit_norm in lbl_norm or lbl_norm in crit_norm:
                return resp

    if index is not None and 0 <= index < len(all_responses):
        return all_responses[index]

    return None


def calculate_vulnerability_score(beneficiary):
    """
    Calcule le score de vulnérabilité d'un bénéficiaire selon les critères du projet.

    Le score correspond à la part des poids vulnérables dans le total des poids
    actifs, ramenée sur 100. Le total des poids n'a donc pas besoin d'être 100.
    """
    from decimal import Decimal

    try:
        campagne = getattr(beneficiary, "campagne", None)
        if not campagne:
            return Decimal("0")

        project = _get_project_from_campaign(campagne)
        if not project:
            return Decimal("0")

        criteria = list(project.criteres.filter(actif=True).select_related("question").order_by("id"))
        if not criteria:
            return Decimal("0")

        responses = list(beneficiary.responses.select_related("question").all())
        if not responses:
            return Decimal("0")

        responses_by_qid = {
            str(r.question_id): r for r in responses if r.question_id
        }
        responses_by_label = {
            normalize_region_name(r.question.label): r for r in responses if r.question and r.question.label
        }

        total_weight = sum((Decimal(str(criterion.poids or 0)) for criterion in criteria), Decimal("0"))
        if total_weight <= 0:
            return Decimal("0")

        score = Decimal("0")

        for idx, criterion in enumerate(criteria):
            response = _find_response_for_criterion(
                criterion,
                responses_by_qid,
                responses_by_label,
                responses,
                index=idx,
            )
            if response and _evaluate_vulnerability(response, criterion):
                score += Decimal(str(criterion.poids or 0))

        normalized_score = (score / total_weight) * Decimal("100")
        return min(normalized_score, Decimal("100")).quantize(Decimal("0.01"))

    except Exception as e:
        logger.error(f"Score calculation failed for beneficiary {beneficiary.id}: {e}")
        return Decimal("0")


def _evaluate_vulnerability(response, criterion) -> bool:
    """
    Évalue si une réponse indique une vulnérabilité pour le critère donné.
    """
    if response is None:
        return False

    valeur = _extraire_valeur_reponse(response)
    if valeur is None:
        return False

    # 1. Si valeur booléenne
    if isinstance(valeur, bool):
        if criterion.vulnerable_values:
            val_str = "oui" if valeur else "non"
            return _check_vulnerability(val_str, criterion.vulnerable_values, getattr(criterion, "vulnerable_operator", "contains") or "contains")
        return valeur is True

    # 2. Si configuration spécifique sur le critère
    if criterion.vulnerable_values and criterion.vulnerable_operator:
        return _check_vulnerability(valeur, criterion.vulnerable_values, criterion.vulnerable_operator)

    # 3. Logique par défaut (détection des réponses positives / Oui)
    return _default_vulnerability_check(response)


def _check_vulnerability(valeur, vulnerable_values, operator) -> bool:
    """Vérifie la vulnérabilité selon l'opérateur et les valeurs configurées."""
    if valeur is None:
        return False

    val_str = str(valeur).strip().lower()
    vuln_lowered = [str(v).strip().lower() for v in vulnerable_values]

    if operator == "equals":
        return val_str in vuln_lowered or (val_str in {"oui", "true", "1", "yes"} and any(v in {"oui", "true", "1", "yes"} for v in vuln_lowered))

    if operator == "contains":
        return any(v in val_str or val_str in v for v in vuln_lowered)

    if operator == "in":
        return val_str in vuln_lowered

    if operator == "lt":
        try:
            return float(valeur) < float(vulnerable_values[0])
        except (ValueError, TypeError, IndexError):
            return False

    if operator == "gt":
        try:
            return float(valeur) > float(vulnerable_values[0])
        except (ValueError, TypeError, IndexError):
            return False

    return val_str in vuln_lowered


def _default_vulnerability_check(response) -> bool:
    """Logique par défaut pour détecter une réponse affirmative / vulnérable."""
    if response.value_boolean is not None:
        return response.value_boolean is True

    if response.value_number is not None:
        val = float(response.value_number)
        return val == 1.0 or val > 0

    if response.value_text is not None and response.value_text != "":
        texte = str(response.value_text).lower().strip()
        if texte in {"oui", "yes", "true", "1", "vrai", "on", "ok"}:
            return True
        vulnerable_keywords = {
            "oui", "yes", "true", "1", "handicap", "malade", "maladie",
            "faible", "très faible", "tres faible", "sans emploi", "chomeur",
            "sans soutien", "manque", "fragile", "difficulte", "besoins",
            "moins de 5", "moins de 5 ans", "enfant", "personne âgée",
            "personne agee", "foyer nombreux", "veuf", "veuve", "orphelin",
            "déplacé", "deplace", "réfugié", "refugie", "sans abri",
            "sans domicile", "chronique", "grave", "critique", "severe",
            "analphabete", "non scolarise", "sans revenu", "pauvre"
        }
        return any(kw in texte for kw in vulnerable_keywords)

    if response.value_json is not None:
        val_json = response.value_json
        if isinstance(val_json, bool):
            return val_json is True
        val_str = str(val_json).lower().strip()
        return any(k in val_str for k in ["oui", "yes", "true", "1", "vrai"])

    return False


def _extraire_valeur_reponse(response):
    """
    Extrait la valeur lisible d'une FormResponse.
    """
    if response.value_boolean is not None:
        return response.value_boolean
    if response.value_number is not None:
        return response.value_number
    if response.value_text is not None and response.value_text != "":
        return response.value_text
    if response.value_json is not None:
        return response.value_json
    if response.value_date is not None:
        return response.value_date
    return None


def _est_reponse_vulnerable(valeur):
    """
    Détermine si une valeur indique une vulnérabilité.
    """
    if valeur is None:
        return False

    if isinstance(valeur, bool):
        return valeur is True

    if isinstance(valeur, (int, float, Decimal)):
        return float(valeur) == 1.0 or float(valeur) > 0

    texte = str(valeur).lower().strip()
    if texte in {"oui", "yes", "true", "1", "vrai", "on", "ok"}:
        return True
    valeurs_vulnerables = [
        "oui", "true", "1", "handicap", "malade", "maladie",
        "faible", "très faible", "tres faible", "sans emploi",
        "moins de 5", "moins de 5 ans", "enfant", "personne âgée",
        "personne agee", "foyer nombreux", "veuf", "orphelin",
        "déplacé", "deplace", "réfugié", "refugie", "sans abri",
        "sans domicile", "chronique", "grave", "critique",
    ]
    return any(v in texte for v in valeurs_vulnerables)


def update_vulnerability_score(beneficiary):
    """
    Met à jour le score de vulnérabilité d'un bénéficiaire.
    Args:
        beneficiary: Instance de Beneficiary
    Returns:
        Beneficiary: Le bénéficiaire avec score mis à jour
    """
    score = calculate_vulnerability_score(beneficiary)
    beneficiary.score_vulnerabilite = score
    beneficiary.save(update_fields=["score_vulnerabilite", "updated_at"])
    return beneficiary


# ─────────────────────────────────────────────────────────────────────────────
# Carte des Priorités — Calcul des scores par région
# ─────────────────────────────────────────────────────────────────────────────

def _get_niveau_et_couleur(score):
    """Retourne le niveau et la couleur selon le score."""
    score_int = int(score or 0)
    if score_int >= 80:
        return "Très élevée", "red"
    elif score_int >= 60:
        return "Élevée", "orange"
    elif score_int >= 40:
        return "Moyenne", "yellow"
    else:
        return "Faible", "green"


def normalize_region_name(value):
    # Normalise un nom de region pour des comparaisons fiables.
    # Zone.region / Project.region sont des champs texte libres : « Thiès »,
    # « Thies », « SAINT-LOUIS », « saint louis »... alors que la carte SVG
    # (GeoJSON) utilise des noms normalises. Sans normalisation, un clic sur
    # « Thiès » ne retrouve aucune zone saisie « Thies ».
    # Retourne : sans accents, minuscules, tirets/underscores -> espaces.
    import unicodedata
    if not value:
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(c for c in text if not unicodedata.combining(c))
    space = chr(32)
    text = text.replace("-", space).replace("_", space)
    return " ".join(text.lower().split())


def _region_variants(region_name):
    # Retourne les variantes de saisie probables d'un nom de region.
    normalized = normalize_region_name(region_name)
    if not normalized:
        return []
    return [
        value
        for value in {region_name, normalized, normalized.title(), normalized.capitalize()}
        if value
    ]


def _region_ids_for_name(region_name):
    """Resolve les variantes lisibles d'une région vers les IDs du modèle Region."""
    variants = set(_region_variants(region_name))
    if not variants:
        return []
    return [
        region.pk
        for region in Region.objects.only("id", "nom")
        if region.nom in variants
        or normalize_region_name(region.nom) == normalize_region_name(region_name)
    ]


def _generer_summary(region_name, zones, total_beneficiaires):
    """
    Génère automatiquement un résumé intelligent de la région.

    Args:
        region_name: Nom de la région
        zones: Liste de zones triées par score décroissant (chaque zone est un dict)
        total_beneficiaires: Nombre total de bénéficiaires dans la région

    Returns:
        str: Résumé textuel formaté
    """
    nb_zones = len(zones)
    zone_labels = {1: "zone", "plural": "zones"}
    label_zone = zone_labels[1] if nb_zones == 1 else zone_labels["plural"]

    summary = (
        f"La région de {region_name} regroupe {total_beneficiaires} bénéficiaire"
        f"{'s' if total_beneficiaires > 1 else ''} répartis dans {nb_zones} {label_zone}."
    )

    if zones:
        zone_top = zones[0]
        score_top = zone_top.get("score_moyen", 0)
        if score_top is None:
            summary += " Les scores de priorité ne sont pas disponibles dans les données fournies."
        elif score_top >= 60:
            summary += (
                f" {zone_top['nom']} présente le score moyen le plus élevé"
                f" ({score_top}/100) et constitue la première priorité d'intervention."
            )
        elif score_top >= 40:
            summary += (
                f" {zone_top['nom']} est la zone la plus prioritaire avec un score"
                f" de {score_top}/100."
            )

        # Mentionner les zones urgentes suivantes
        urgentes = [
            z for z in zones[1:3]
            if z.get("score_moyen") is not None and z["score_moyen"] >= 40
        ]
        if urgentes:
            noms = " et ".join(z["nom"] for z in urgentes)
            verb = "nécessitent" if len(urgentes) > 1 else "nécessite"
            summary += f" {noms} {verb} également une intervention dans les prochains jours."

    return summary

def _generer_observations(region_name, zones, total_beneficiaires):
    # Genere une liste d'observations factuelles a partir des donnees calculees.
    observations = []
    if not zones:
        return observations
    scored_zones = [zone for zone in zones if zone.get("score_moyen") is not None]
    if not scored_zones:
        return ["Information non disponible dans les données fournies."]
    tres_elevees = [
        b
        for z in zones
        for b in z.get("beneficiaires", [])
        if (b.get("score") or 0) >= 80
    ]
    if tres_elevees:
        observations.append(
            f"{len(tres_elevees)} bénéficiaire"
            f"{'s sont classés' if len(tres_elevees) > 1 else ' est classé'} "
            "Très élevée."
        )

    zone_top = scored_zones[0]
    observations.append(
        f"{zone_top['nom']} concentre la vulnérabilité la plus forte "
        f"(score moyen {zone_top.get('score_moyen', 0)}/100)."
    )

    if len(scored_zones) > 1:
        zone_2 = scored_zones[1]
        observations.append(
            f"{zone_2['nom']} représente la deuxième zone prioritaire "
            f"(score moyen {zone_2.get('score_moyen', 0)}/100)."
        )

    return observations

def _generer_recommandations(region_name, zones, total_beneficiaires):
    # Genere des recommandations actionnables, sans justification detaillee.
    recommandations = []
    if not zones:
        return [
            "Programmer une collecte terrain dans cette région.",
        ]

    scored_zones = [zone for zone in zones if zone.get("score_moyen") is not None]
    if not scored_zones:
        return ["Information non disponible dans les données fournies."]

    zone_top = scored_zones[0]
    recommandations.append(
        f"Prioriser les distributions à {zone_top['nom']}."
    )

    if len(scored_zones) > 1:
        recommandations.append(
            f"Renforcer l'équipe terrain à {scored_zones[1]['nom']}."
        )

    recommandations.append(
        "Mettre à jour les bénéficiaires avant la prochaine mission."
    )

    return recommandations


def _get_criteres_beneficiaire(beneficiary, criteria_list):
    """
    Retourne la liste des critères avec la réponse et les points obtenus
    pour un bénéficiaire donné (utilisé par la Carte des Priorités).

    Args:
        beneficiary: Instance de Beneficiary (avec responses prefetched)
        criteria_list: Liste des critères actifs du projet

    Returns:
        list[dict]: [{nom, reponse, points, poids_max, obtenu}]
    """
    responses = list(beneficiary.responses.select_related("question").all())
    responses_by_qid = {
        str(r.question_id): r for r in responses if r.question_id
    }
    responses_by_label = {
        normalize_region_name(r.question.label): r for r in responses if r.question and r.question.label
    }

    criteres_detail = []
    for idx, criterion in enumerate(criteria_list):
        response = _find_response_for_criterion(
            criterion,
            responses_by_qid,
            responses_by_label,
            responses,
            index=idx,
        )
        if response:
            is_vulnerable = _evaluate_vulnerability(response, criterion)
            points = criterion.poids if is_vulnerable else 0

            # Formatter la réponse lisible
            valeur = _extraire_valeur_reponse(response)
            if isinstance(valeur, bool):
                reponse_lisible = "Oui" if valeur else "Non"
            elif valeur is None:
                reponse_lisible = "—"
            else:
                reponse_lisible = str(valeur)
        else:
            is_vulnerable = False
            points = 0
            reponse_lisible = "—"

        criteres_detail.append({
            "nom": criterion.nom,
            "reponse": reponse_lisible,
            "points": points,
            "poids_max": criterion.poids,
            "obtenu": is_vulnerable,
        })

    return criteres_detail


def _calculer_age(date_naissance):
    """Calcule l'âge à partir de la date de naissance."""
    from django.utils import timezone as tz
    today = tz.now().date()
    try:
        age = today.year - date_naissance.year - (
            (today.month, today.day) < (date_naissance.month, date_naissance.day)
        )
        return age
    except Exception:
        return None


def region_exists_in_project(project, region_name):
    """
    Indique si une region existe pour un projet donne.

    Une region est consideree comme existante si au moins une zone du projet
    (ou un beneficiaire du projet) lui est rattachee, ou si elle correspond
    a la region declaree du projet.
    """
    region_normalized = normalize_region_name(region_name)
    if not region_normalized:
        return False

    # La carte et le détail doivent partager la même source d'éligibilité :
    # le projet, les bénéficiaires de ses campagnes et les zones de son ONG.
    # Cela évite qu'une région visible sur la carte soit rejetée au clic.
    return any(
        normalize_region_name(item.get("region")) == region_normalized
        for item in build_all_regions_scores(project)
    )


def _get_region_zones(project, region_name):
    # Toutes les zones d'une region pour un projet donne.
    #
    # Sources (dans l'ordre de priorite) :
    #   1) les zones rattachees aux campagnes du projet ;
    #   2) a defaut, les zones de l'ONG dans cette region.
    #
    # Ces zones doivent etre renvoyees meme sans aucun beneficiaire afin que le
    # panneau lateral affiche l'integralite de la region (score 0 / 0 ben.).
    region_ids = _region_ids_for_name(region_name)
    if not region_ids:
        return []

    from apps.campaigns.models import Campaign
    project_zone_ids = (
        Campaign.objects
        .filter(
            projet=project,
            organization_id=project.organization_id,
            projet__organization_id=project.organization_id,
        )
        .values_list("zones__id", flat=True)
    )
    zones = list(
        Zone.objects
        .filter(
            id__in=project_zone_ids,
            region_id__in=region_ids,
            organization_id=project.organization_id,
        )
        .order_by("nom")
    )
    if zones:
        return zones
    # Fallback : aucune campagne/zone rattachee au projet pour cette region.
    return list(
        Zone.objects
        .filter(
            organization_id=project.organization_id,
            region_id__in=region_ids,
        )
        .order_by("nom")
    )


def build_region_priorities(project, region_name):
    """
    Construit les données de priorité pour une région donnée dans un projet.

    Args:
        project: Instance de Project
        region_name: Nom de la région (string)

    Returns:
        dict: {region, summary, score_region, total_beneficiaires, zones}
    """
    # Critères actifs du projet (avec question liée)
    criteria_list = list(
        project.criteres.filter(actif=True).select_related("question")
    )

    # Tous les bénéficiaires du projet dans cette région (matching tolerant :
    # « Thiès » retrouve les zones saisies « Thies »).
    beneficiaries = (
        Beneficiary.objects
        .filter(
            campagne__projet=project,
            organization_id=project.organization_id,
            campagne__organization_id=project.organization_id,
            campagne__projet__organization_id=project.organization_id,
            zone__organization_id=project.organization_id,
            zone__region_id__in=_region_ids_for_name(region_name),
        )
        .select_related("zone", "campagne")
        .prefetch_related("responses__question")
        .order_by("-score_vulnerabilite")
    )

    # Toutes les zones de la region (celles rattachees aux campagnes du projet,
    # sinon celles de l'ONG). Elles doivent apparaitre meme sans beneficiaire.
    region_zones = _get_region_zones(project, region_name)

    # Pre-remplissage : une entree par zone de la region (0 beneficiaire par defaut).
    zones_data = {}
    for zone in region_zones:
        zones_data[str(zone.id)] = {
            "id": str(zone.id),
            "nom": zone.nom,
            "zone": zone,
            "scores": [],
            "beneficiaires": [],
        }

    # Regroupement des beneficiaires par zone
    for b in beneficiaries:
        zone = b.zone
        if zone is None:
            # Bénéficiaire orphelin de zone : ignoré, il ne fausse pas les scores
            continue
        zone_id = str(zone.id)
        if zone_id not in zones_data:
            # Beneficiaire rattache a une zone hors du perimetre connu : on la
            # cree a la volee pour ne rien perdre.
            zones_data[zone_id] = {
                "id": zone_id,
                "nom": zone.nom,
                "zone": zone,
                "scores": [],
                "beneficiaires": [],
            }

        score_b = int(b.score_vulnerabilite) if b.score_vulnerabilite is not None else None
        if score_b is not None:
            zones_data[zone_id]["scores"].append(score_b)

        age = _calculer_age(b.date_naissance)
        criteres_detail = _get_criteres_beneficiaire(b, criteria_list)
        niveau_b, _ = _get_niveau_et_couleur(score_b) if score_b is not None else (None, "grey")

        zones_data[zone_id]["beneficiaires"].append({
            "id": str(b.id),
            "nom_complet": f"{b.prenom} {b.nom}",
            "nom": b.nom,
            "prenom": b.prenom,
            "telephone": b.telephone,
            "sexe": b.sexe,
            "age": age,
            "date_naissance": str(b.date_naissance),
            "quartier": b.zone.departement.nom if b.zone and b.zone.departement_id else "",
            "region": b.zone.region.nom if b.zone and b.zone.region_id else region_name,
            "zone_nom": b.zone.nom if b.zone else "",
            "score": score_b,
            "niveau": niveau_b,
            "criteres": criteres_detail,
        })

    # Construire la liste des zones triées par score moyen décroissant
    zones_list = []
    for zone_id, data in zones_data.items():
        scores = data["scores"]
        score_moyen = round(sum(scores) / len(scores)) if scores else None
        niveau_zone, couleur_zone = _get_niveau_et_couleur(score_moyen) if score_moyen is not None else (None, "grey")

        # Trier les bénéficiaires par score décroissant
        bens_sorted = sorted(data["beneficiaires"], key=lambda x: x["score"] if x["score"] is not None else -1, reverse=True)

        zones_list.append({
            "id": zone_id,
            "nom": data["nom"],
            # Alias compatibles avec le contrat JSON attendu (score / beneficiaires).
            "score": score_moyen,
            "beneficiaires_count": len(bens_sorted),
            "score_moyen": score_moyen,
            "niveau": niveau_zone,
            "couleur": couleur_zone,
            "latitude": str(data["zone"].latitude) if data.get("zone") else None,
            "longitude": str(data["zone"].longitude) if data.get("zone") else None,
            "rayon": data["zone"].rayon if data.get("zone") else None,
            "region": data["zone"].region.nom if data.get("zone") else region_name,
            "total_beneficiaires": len(bens_sorted),
            "beneficiaires": bens_sorted,
        })

    zones_list.sort(key=lambda z: (z["score_moyen"] is None, -(z["score_moyen"] or 0)))

    # Score moyen de la région
    all_scores = [b["score"] for z in zones_list for b in z["beneficiaires"] if b.get("score") is not None]
    score_region = round(sum(all_scores) / len(all_scores)) if all_scores else None
    total_beneficiaires = sum(zone["total_beneficiaires"] for zone in zones_list)

    summary = _generer_summary(region_name, zones_list, total_beneficiaires)
    observations = _generer_observations(region_name, zones_list, total_beneficiaires)
    recommandations = _generer_recommandations(region_name, zones_list, total_beneficiaires)
    niveau_region, couleur_region = _get_niveau_et_couleur(score_region) if score_region is not None else (None, "grey")

    return {
        "region": region_name,
        "summary": summary,
        "observations": observations,
        "recommandations": recommandations,
        "score_region": score_region,
        "niveau_region": niveau_region,
        "couleur_region": couleur_region,
        "total_beneficiaires": total_beneficiaires,
        "nb_zones": len(zones_list),
        "zones": zones_list,
    }


def build_all_regions_scores(project):
    """
    Retourne la liste de toutes les régions avec leur score agrégé
    pour coloriser la carte SVG du Sénégal.

    Args:
        project: Instance de Project

    Returns:
        list[dict]: [{region, score, total_beneficiaires, niveau, couleur}]
    """
    from django.db.models import Avg, Count
    # 1) Regions ayant des bénéficiaires collectés sur ce projet (score agrégé)
    result = (
        Beneficiary.objects
        .filter(campagne__projet=project)
        .filter(
            organization_id=project.organization_id,
            campagne__organization_id=project.organization_id,
            campagne__projet__organization_id=project.organization_id,
            zone__organization_id=project.organization_id,
        )
        .values("zone__region__nom")
        .annotate(
            score_moyen=Avg("score_vulnerabilite"),
            total=Count("id"),
        )
        .order_by("-score_moyen")
    )

    # Index par nom normalisé pour fusionner sans doublon les variantes de saisie.
    regions_by_key = {}
    for row in result:
        region_name = row["zone__region__nom"] or "Inconnue"
        raw_score = row["score_moyen"]
        score = round(raw_score) if raw_score is not None else 0
        niveau, couleur = _get_niveau_et_couleur(score) if raw_score is not None else ("Aucune donnée", "grey")
        key = normalize_region_name(region_name)
        regions_by_key[key] = {
            "region": region_name,
            "score": score,
            "score_region": score,
            "total_beneficiaires": row["total"],
            "niveau": niveau,
            "couleur": couleur,
        }

    # 2) Regions declarees sur le projet ou portant des zones de l'organisation :
    #    elles doivent apparaître sur la carte même sans bénéficiaire (score 0).
    declared_names = []
    if project.region:
        declared_names.append(project.region)
    declared_names.extend(
        Zone.objects
        .filter(organization_id=project.organization_id)
        .values_list("region__nom", flat=True)
        .distinct()
    )

    for region_name in declared_names:
        if not region_name:
            continue
        key = normalize_region_name(region_name)
        if key in regions_by_key:
            continue
        regions_by_key[key] = {
            "region": region_name,
            "score": 0,
            "score_region": 0,
            "total_beneficiaires": 0,
            "niveau": "Aucune donnée",
            "couleur": "grey",
        }

    # Les zones exposées sur la carte sont strictement celles rattachées aux
    # campagnes de ce projet. Le score est agrégé depuis les scores Django.
    project_zones = list(
        Zone.objects
        .filter(
            organization_id=project.organization_id,
            campaigns__projet=project,
            campaigns__organization_id=project.organization_id,
            campaigns__projet__organization_id=project.organization_id,
        )
        .select_related("region")
        .distinct()
        .order_by("nom", "pk")
    )
    zone_scores = {
        row["zone_id"]: row
        for row in (
            Beneficiary.objects
            .filter(
                campagne__projet=project,
                organization_id=project.organization_id,
                campagne__organization_id=project.organization_id,
                campagne__projet__organization_id=project.organization_id,
                zone__organization_id=project.organization_id,
                zone_id__in=[zone.pk for zone in project_zones],
            )
            .values("zone_id")
            .annotate(score_moyen=Avg("score_vulnerabilite"), total=Count("id"))
        )
    }
    for zone in project_zones:
        region_key = normalize_region_name(zone.region.nom)
        region_data = regions_by_key.get(region_key)
        if region_data is None:
            continue
        score_data = zone_scores.get(zone.pk, {})
        raw_score = score_data.get("score_moyen")
        score = round(raw_score) if raw_score is not None else None
        niveau, couleur = _get_niveau_et_couleur(score) if score is not None else (None, "grey")
        region_data.setdefault("zones", []).append({
            "id": str(zone.pk),
            "nom": zone.nom,
            "region": zone.region.nom,
            "latitude": str(zone.latitude) if zone.latitude is not None else None,
            "longitude": str(zone.longitude) if zone.longitude is not None else None,
            "rayon": zone.rayon,
            "score": score,
            "score_moyen": score,
            "niveau": niveau,
            "couleur": couleur,
            "total_beneficiaires": score_data.get("total", 0),
        })

    for region_data in regions_by_key.values():
        region_data.setdefault("zones", [])

    # Tri : régions avec bénéficiaires d'abord, par score décroissant.
    regions_list = sorted(
        regions_by_key.values(),
        key=lambda r: (r["total_beneficiaires"] == 0, -(r["score"] or 0)),
    )

    return regions_list


def get_zone_beneficiaries_table_data(zone_id, user, project_id=None, params=None):
    """
    Retourne la liste complète des bénéficiaires d'une zone avec scores,
    informations personnelles et détails des critères répondus.
    """
    from apps.zones.models import Zone
    from apps.projects.models import Project, ProjectCriteria
    from django.core.paginator import Paginator
    from django.db.models import Avg, Q

    params = params or {}

    zone = Zone.objects.filter(id=zone_id).first()
    if not zone:
        raise BeneficiaryError("Zone introuvable.")

    if user.role != "SUPER_ADMIN" and zone.organization != user.organization:
        raise BeneficiaryError("Cette zone n'appartient pas à votre ONG.")

    beneficiaries = (
        Beneficiary.objects
        .filter(
            zone=zone,
            organization_id=zone.organization_id,
            campagne__organization_id=zone.organization_id,
            campagne__projet__organization_id=zone.organization_id,
        )
        .select_related("campagne__projet", "created_by", "zone__region", "zone__departement")
        .prefetch_related("responses__question")
        .order_by("-score_vulnerabilite")
    )

    if project_id:
        try:
            project_id = int(project_id)
        except (TypeError, ValueError):
            raise BeneficiaryError("Identifiant de projet invalide.")
        projects = Project.objects.filter(
            pk=project_id,
            organization_id=zone.organization_id,
            archived=False,
        )
        if user.role == "CHEF_PROJET":
            projects = projects.filter(chef_projet=user)
        project = projects.first()
        if not project:
            raise BeneficiaryError("Projet introuvable dans votre périmètre.")
        beneficiaries = beneficiaries.filter(campagne__projet=project)

    if user.role == "CHEF_PROJET":
        beneficiaries = beneficiaries.filter(
            Q(campagne__projet__chef_projet=user) | Q(created_by=user)
        )
    elif user.role == "AGENT":
        assignments = list(
            CampagneAffectation.objects.filter(
                agent=user,
                campagne__organization_id=zone.organization_id,
                campagne__projet__organization_id=zone.organization_id,
                zone=zone.nom,
            ).values_list("campagne_id", "zone")
        )
        assignment_scope = Q(pk__in=[])
        for campaign_id, assigned_zone in assignments:
            assignment_scope |= Q(campagne_id=campaign_id, zone__nom=assigned_zone)
        beneficiaries = beneficiaries.filter(assignment_scope)

    scoped_total = beneficiaries.count()
    score_average = beneficiaries.exclude(
        score_vulnerabilite__isnull=True,
    ).aggregate(average=Avg("score_vulnerabilite"))["average"] or 0

    search = (params.get("search") or "").strip()
    if search:
        beneficiaries = beneficiaries.filter(
            Q(nom__icontains=search)
            | Q(prenom__icontains=search)
            | Q(telephone__icontains=search)
            | Q(zone__departement__nom__icontains=search)
        )

    level = params.get("niveau")
    if level == "Très élevée":
        beneficiaries = beneficiaries.filter(score_vulnerabilite__gte=80)
    elif level == "Élevée":
        beneficiaries = beneficiaries.filter(score_vulnerabilite__gte=60, score_vulnerabilite__lt=80)
    elif level == "Moyenne":
        beneficiaries = beneficiaries.filter(score_vulnerabilite__gte=40, score_vulnerabilite__lt=60)
    elif level == "Faible":
        beneficiaries = beneficiaries.filter(Q(score_vulnerabilite__lt=40) | Q(score_vulnerabilite__isnull=True))

    ordering = {
        "score_asc": ("score_vulnerabilite", "nom", "prenom"),
        "nom_asc": ("prenom", "nom"),
        "nom_desc": ("-prenom", "-nom"),
        # Birth date ascending means older beneficiaries appear first.
        "age_desc": ("date_naissance", "nom", "prenom"),
    }.get(params.get("sort"), ("-score_vulnerabilite", "nom", "prenom"))
    beneficiaries = beneficiaries.order_by(*ordering)

    try:
        page_size = min(max(int(params.get("page_size", 20)), 1), 100)
    except (TypeError, ValueError):
        page_size = 20
    paginator = Paginator(beneficiaries, page_size)
    page_obj = paginator.get_page(params.get("page", 1))

    # Récupérer les critères des projets concernés
    project_ids = list(
        beneficiaries.exclude(campagne__projet__isnull=True)
        .values_list("campagne__projet_id", flat=True)
        .distinct()
    )
    criteria_list = []
    if project_ids:
        criteria_list = list(
            ProjectCriteria.objects
            .filter(projet_id__in=project_ids, actif=True)
            .select_related("question")
        )

    bens_data = []
    scores = []
    for b in page_obj.object_list:
        score_val = int(b.score_vulnerabilite or 0)
        scores.append(score_val)
        age = _calculer_age(b.date_naissance)
        niveau, couleur = _get_niveau_et_couleur(score_val)

        # Critères évalués pour ce bénéficiaire
        criteres_detail = _get_criteres_beneficiaire(b, criteria_list)

        # Réponses brutes
        raw_responses = []
        for r in b.responses.all():
            val = _extraire_valeur_reponse(r)
            raw_responses.append({
                "id": str(r.id),
                "question": r.question.label if r.question else "",
                "type": r.question.type if r.question else "text",
                "valeur": val,
            })

        bens_data.append({
            "id": str(b.id),
            "nom": b.nom,
            "prenom": b.prenom,
            "nom_complet": f"{b.prenom} {b.nom}".strip(),
            "telephone": b.telephone,
            "sexe": b.sexe,
            "date_naissance": str(b.date_naissance) if b.date_naissance else "",
            "age": age,
            "quartier": zone.departement.nom if zone.departement_id else zone.nom,
            "region": zone.region.nom if zone.region_id else "",
            "zone_nom": zone.nom,
            "score": score_val,
            "niveau": niveau,
            "couleur": couleur,
            "criteres": criteres_detail,
            "responses": raw_responses,
            "campagne": {
                "id": str(b.campagne.id),
                "nom": b.campagne.nom,
            } if b.campagne else None,
            "created_at": b.created_at.isoformat() if hasattr(b, "created_at") and b.created_at else "",
        })

    score_moyen = round(float(score_average)) if scoped_total else 0
    niveau_moyen, couleur_moyen = _get_niveau_et_couleur(score_moyen)

    return {
        "zone": {
            "id": str(zone.id),
            "nom": zone.nom,
            "region": zone.region.nom if zone.region_id else "",
            "departement": zone.departement.nom if zone.departement_id else zone.nom,
            "score_moyen": score_moyen,
            "niveau": niveau_moyen,
            "couleur": couleur_moyen,
            "total_beneficiaires": scoped_total,
        },
        "beneficiaires": bens_data,
        "pagination": {
            "count": paginator.count,
            "page": page_obj.number,
            "page_size": page_size,
            "num_pages": paginator.num_pages,
            "next": page_obj.next_page_number() if page_obj.has_next() else None,
            "previous": page_obj.previous_page_number() if page_obj.has_previous() else None,
        },
        "criteres_projet": [
            {
                "id": str(c.id),
                "nom": c.nom,
                "poids": c.poids,
                "question": c.question.label if c.question else "",
            }
            for c in criteria_list
        ],
    }
