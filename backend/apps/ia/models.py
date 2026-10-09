import uuid
from django.db import models
from django.conf import settings
from apps.campaigns.models import Campaign


class IAnalyse(models.Model):
    """
    Modèle pour stocker les résultats d'analyses IA.
    """
    class TypeAnalyse(models.TextChoices):
        GLOBAL = 'global', 'Analyse Globale'
        EXECUTIVE = 'executive', 'Executive Insight'
        FINANCE = 'finance', 'Analyse Financière'
        ZONES = 'zones', 'Analyse Zones'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campagne = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='ia_analyses'
    )
    type_analyse = models.CharField(
        max_length=20,
        choices=TypeAnalyse.choices,
        default=TypeAnalyse.GLOBAL
    )
    response_data = models.JSONField(default=dict)
    donnees_entree = models.JSONField(default=dict, blank=True)
    recommandation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ia_ianalyse'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['campagne', 'type_analyse']),
        ]

    def __str__(self):
        return f"{self.type_analyse} - {self.campagne.nom}"


class AssistantInteraction(models.Model):
    """Audit trail for the Gerant's conversational assistant."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation_id = models.UUIDField(db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE, null=True, blank=True
    )
    request_text = models.TextField()
    response_text = models.TextField()
    tools_used = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Assistant interaction {self.id} ({self.user_id})"
