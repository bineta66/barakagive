import uuid

from django.db import models
from django.conf import settings


class Campaign(models.Model):
    """
    Modèle représentant une campagne humanitaire.
    Une campagne appartient à un projet et peut couvrir plusieurs zones.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    projet = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="campaigns",
    )

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="campaigns",
    )

    nom = models.CharField(max_length=200)

    code_campagne = models.CharField(max_length=30, unique=True, blank=True, editable=False)

    description = models.TextField()

    zones = models.ManyToManyField(
        "zones.Zone",
        related_name="campaigns",
        blank=True,
    )

    date_debut = models.DateField()

    date_fin = models.DateField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_campaigns",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code_campagne} - {self.nom}"

    class Meta:
        verbose_name = "Campagne"
        verbose_name_plural = "Campagnes"
        ordering = ["-created_at"]