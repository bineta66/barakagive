from django.urls import path
from .views import (
    SubscriptionStatusView,
    SubscriptionDetailView,
    InitiatePaymentView,
    PaymentWebhookView,
    TransactionHistoryView,
    SubscriptionCheckView,
)

urlpatterns = [
    # État de l'abonnement (pour banner, dashboard)
    path("subscription/", SubscriptionStatusView.as_view(), name="subscription-status"),
    path("subscription/detail/", SubscriptionDetailView.as_view(), name="subscription-detail"),
    path("subscription/check/", SubscriptionCheckView.as_view(), name="subscription-check"),

    # Paiement
    path("subscribe/", InitiatePaymentView.as_view(), name="initiate-payment"),

    # Webhook PayTech
    path("webhook/", PaymentWebhookView.as_view(), name="payment-webhook"),

    # Historique
    path("history/", TransactionHistoryView.as_view(), name="transaction-history"),
]