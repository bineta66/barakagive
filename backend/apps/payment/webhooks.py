"""
Webhooks PayTech - Logique séparée pour clarté.
Le webhook principal est dans views.py (PaymentWebhookView).
Ce fichier contient les helpers pour traiter les webhooks.
"""

import logging
from django.utils import timezone
from .models import Transaction, Subscription
from .services import paytech_service

logger = logging.getLogger(__name__)


def process_paytech_webhook(data: dict) -> dict:
    """
    Traite un webhook PayTech.
    Retourne un dict avec le résultat du traitement.
    """
    transaction_id = data.get("ref_command") or data.get("transaction_id")

    if not transaction_id:
        return {"success": False, "error": "Transaction ID manquant"}

    try:
        transaction = Transaction.objects.select_related("subscription").get(
            transaction_id=transaction_id
        )
    except Transaction.DoesNotExist:
        logger.warning(f"Transaction {transaction_id} introuvable")
        return {"success": False, "error": "Transaction introuvable"}

    if transaction.statut == Transaction.Statut.SUCCESS:
        return {"success": True, "message": "Déjà traité"}

    verification = paytech_service.verify_payment(transaction_id)
    if verification.get("verification_unavailable"):
        return {"success": False, "error": "Vérification du paiement indisponible"}
    if verification.get("success") != 1:
        return {"success": False, "error": "Paiement non confirmé par PayTech"}
    return handle_successful_payment(transaction, data, verification=verification)


def handle_successful_payment(transaction: Transaction, data: dict, verification=None) -> dict:
    """Traite un paiement réussi."""
    if transaction.statut == "SUCCESS":
        return {"success": True, "message": "Déjà traité"}

    if verification is None:
        verification = paytech_service.verify_payment(transaction.transaction_id)
    if verification.get("verification_unavailable") or verification.get("success") != 1:
        return {"success": False, "error": "Paiement non confirmé par PayTech"}

    transaction.statut = "SUCCESS"
    transaction.paid_at = timezone.now()
    transaction.raw_data = {**transaction.raw_data, "webhook": data}
    transaction.save(update_fields=["statut", "paid_at", "raw_data", "updated_at"])

    # Activer l'abonnement
    subscription = transaction.subscription
    subscription.activate_subscription()

    logger.info(f"Paiement réussi pour {subscription.ong.name}: {transaction.transaction_id}")
    return {"success": True, "message": "Paiement activé"}


def handle_failed_payment(transaction: Transaction, data: dict) -> dict:
    """Refuse une transition négative issue d'un webhook non authentifié."""
    return {"success": False, "error": "Statut de paiement non vérifié"}


def handle_cancelled_payment(transaction: Transaction, data: dict) -> dict:
    """Refuse une transition négative issue d'un webhook non authentifié."""
    return {"success": False, "error": "Statut de paiement non vérifié"}
