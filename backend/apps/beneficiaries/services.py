from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from apps.campaigns.models import Campaign, CampagneAffectation
from apps.zones.models import Zone
from apps.forms.models import Formulaire, FormField
from .models import Beneficiary, FormResponse


class BeneficiaryError(Exception):
    """Exception personnalisée pour les erreurs de bénéficiaire."""
    pass


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
    if user.role != "AGENT":
        raise BeneficiaryError("Seul un Agent terrain peut créer un bénéficiaire.")

    if not user.organization:
        raise BeneficiaryError("Vous n'appartenez à aucune ONG.")

    if campaign.organization != user.organization:
        raise BeneficiaryError("La campagne n'appartient pas à votre ONG.")

    assignment = CampagneAffectation.objects.filter(
        campagne=campaign,
        agent=user,
    ).first()
    if not assignment:
        raise BeneficiaryError("Vous n'êtes pas affecté à cette campagne.")

    if zone.organization != user.organization:
        raise BeneficiaryError("La zone n'appartient pas à votre ONG.")

    if zone not in campaign.zones.all():
        raise BeneficiaryError("La zone ne fait pas partie de cette campagne.")

    if assignment.zone != zone.nom:
        raise BeneficiaryError("La zone ne correspond pas à votre affectation.")

    if formulaire.campagne != campaign:
        raise BeneficiaryError("Le formulaire n'appartient pas à cette campagne.")

    if formulaire.statut != Formulaire.Statut.PUBLIE:
        raise BeneficiaryError("Le formulaire doit être publié pour être utilisé.")


def check_duplicate_in_campaign(campaign, telephone, nom, prenom, date_naissance, exclude_id=None):
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
    queryset = Beneficiary.objects.filter(campagne=campaign)

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


def check_sync_duplicate(local_id, device_id):
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
    response_data = {
        "beneficiary": beneficiary,
        "formulaire": formulaire,
        "question": question,
    }

    field_type = question.type

    if field_type in [FormField.TypeChoices.TEXT, FormField.TypeChoices.PHONE, FormField.TypeChoices.TEXTAREA]:
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
            response_data["value_boolean"] = value.lower() in ["true", "oui", "yes", "1"]
        else:
            response_data["value_boolean"] = bool(value)

    elif field_type == FormField.TypeChoices.NUMBER:
        try:
            response_data["value_number"] = Decimal(str(value))
        except (ValueError, TypeError):
            response_data["value_number"] = Decimal("0")

    elif field_type == FormField.TypeChoices.DATE:
        if isinstance(value, str):
            from datetime import datetime
            try:
                response_data["value_date"] = datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                pass

    elif field_type == FormField.TypeChoices.GPS:
        # Les coordonnées GPS sont stockées dans Beneficiary, pas dans FormResponse
        # On crée quand même une entrée pour la traçabilité
        response_data["value_json"] = {"latitude": None, "longitude": None}

    return FormResponse.objects.create(**response_data)


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
    campagne_id = validated_data["campagne_id"]
    formulaire_id = validated_data["formulaire_id"]
    zone_id = validated_data["zone_id"]
    local_id = validated_data["local_id"]
    device_id = validated_data["device_id"]
    beneficiary_data = validated_data["beneficiary"]
    responses_data = validated_data["responses"]

    # Récupérer les objets
    try:
        campaign = Campaign.objects.select_related("projet", "organization").get(id=campagne_id)
    except Campaign.DoesNotExist:
        raise BeneficiaryError("La campagne spécifiée n'existe pas.")

    try:
        zone = Zone.objects.get(id=zone_id)
    except Zone.DoesNotExist:
        raise BeneficiaryError("La zone spécifiée n'existe pas.")

    try:
        formulaire = Formulaire.objects.select_related("campagne", "organization").get(id=formulaire_id)
    except Formulaire.DoesNotExist:
        raise BeneficiaryError("Le formulaire spécifié n'existe pas.")

    # Vérifications de permissions
    validate_agent_permissions(user, campaign, zone, formulaire)

    # Vérifier doublon de synchronisation (local_id + device_id)
    sync_duplicate = check_sync_duplicate(local_id, device_id)
    if sync_duplicate:
        raise BeneficiaryError("Ce bénéficiaire a déjà été synchronisé depuis ce dispositif.")

    # Extraire les données personnelles
    telephone = beneficiary_data["telephone"]
    nom = beneficiary_data["nom"]
    prenom = beneficiary_data["prenom"]
    date_naissance = beneficiary_data["date_naissance"]

    # Vérifier doublon dans la campagne
    duplicate = check_duplicate_in_campaign(
        campaign, telephone, nom, prenom, date_naissance
    )
    if duplicate:
        raise BeneficiaryError("Ce bénéficiaire est déjà inscrit dans cette campagne.")

    # Créer le bénéficiaire et les réponses
    with transaction.atomic():
        beneficiary = Beneficiary.objects.create(
            campagne=campaign,
            zone=zone,
            organization=user.organization,
            nom=nom,
            prenom=prenom,
            telephone=telephone,
            sexe=beneficiary_data["sexe"],
            date_naissance=date_naissance,
            latitude=beneficiary_data["latitude"],
            longitude=beneficiary_data["longitude"],
            local_id=local_id,
            device_id=device_id,
            created_by=user,
            sync_status=Beneficiary.SyncStatus.SYNCED,
        )

        # Récupérer toutes les questions du formulaire
        questions = {str(q.id): q for q in formulaire.fields.all()}

        # Créer les réponses
        created_responses = []
        for resp_data in responses_data:
            question_id = str(resp_data["question_id"])
            value = resp_data["value"]

            if question_id not in questions:
                raise BeneficiaryError(f"Question {question_id} non trouvée dans ce formulaire.")

            question = questions[question_id]
            response = store_response(beneficiary, formulaire, question, value)
            created_responses.append(response)

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
                    "local_id": str(data["local_id"]),
                    "status": "DUPLICATE",
                    "beneficiary_id": str(beneficiary.id),
                })
            else:
                results["synced"] += 1
                results["details"].append({
                    "local_id": str(data["local_id"]),
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


def calculate_ai_score(beneficiary):
    """
    Calcule le score IA d'un bénéficiaire.
    À implémenter selon les critères du projet.

    Args:
        beneficiary: Instance de Beneficiary

    Returns:
        Decimal: Score entre 0 et 100
    """
    # TODO: Implémenter la logique de calcul du score IA
    # Basé sur :
    # - Les réponses (FormResponse)
    # - Les critères du projet (ProjectCriteria)
    # - La campagne
    # - La zone

    # Pour l'instant, retourner un score par défaut
    return Decimal("50.00")


def update_ai_score(beneficiary):
    """
    Met à jour le score IA d'un bénéficiaire.

    Args:
        beneficiary: Instance de Beneficiary

    Returns:
        Beneficiary: Le bénéficiaire avec score mis à jour
    """
    score = calculate_ai_score(beneficiary)
    beneficiary.ai_score = score
    beneficiary.save(update_fields=["ai_score", "updated_at"])
    return beneficiary