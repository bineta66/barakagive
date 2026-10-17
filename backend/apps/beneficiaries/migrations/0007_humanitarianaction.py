import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("beneficiaries", "0006_beneficiary_date_derniere_evaluation_and_more"),
        ("campaigns", "0005_campaign_type"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="HumanitarianAction",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "type_aide",
                    models.CharField(
                        choices=[
                            ("ALIMENTAIRE", "Aide alimentaire"),
                            ("SANTE", "Santé"),
                            ("VETEMENTS", "Vêtements"),
                            ("FOURNITURES", "Fournitures"),
                            ("URGENCE", "Aide d'urgence"),
                            ("AUTRE", "Autre"),
                        ],
                        max_length=20,
                    ),
                ),
                ("date_action", models.DateField()),
                (
                    "quantite",
                    models.DecimalField(decimal_places=2, default=1, max_digits=12),
                ),
                (
                    "statut",
                    models.CharField(
                        choices=[("REALISEE", "Réalisée"), ("ANNULEE", "Annulée")],
                        default="REALISEE",
                        max_length=20,
                    ),
                ),
                ("resultat", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "agent",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="humanitarian_actions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "beneficiary",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="humanitarian_actions",
                        to="beneficiaries.beneficiary",
                    ),
                ),
                (
                    "campagne",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="humanitarian_actions",
                        to="campaigns.campaign",
                    ),
                ),
            ],
            options={
                "ordering": ["-date_action", "-created_at"],
                "indexes": [
                    models.Index(
                        fields=["beneficiary", "date_action"],
                        name="humanact_beneficiary_date_idx",
                    ),
                    models.Index(
                        fields=["campagne", "statut"],
                        name="humanact_campaign_status_idx",
                    ),
                ],
            },
        ),
    ]
