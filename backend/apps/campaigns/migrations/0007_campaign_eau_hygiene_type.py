from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("campaigns", "0006_campaign_operational_types"),
    ]

    operations = [
        migrations.AlterField(
            model_name="campaign",
            name="type",
            field=models.CharField(
                choices=[
                    ("COLLECTE", "Collecte de fonds (ancien type)"),
                    ("COLLECTE_BESOINS", "Collecte des besoins"),
                    ("DISTRIBUTION", "Distribution"),
                    ("SANTE", "Santé / Médical"),
                    ("ALIMENTATION", "Alimentation"),
                    ("EAU_HYGIENE", "Eau et hygiène"),
                    ("SENSIBILISATION", "Sensibilisation"),
                    ("URGENCE", "Urgence"),
                    ("SUIVI_EVALUATION", "Suivi et évaluation"),
                ],
                default="DISTRIBUTION",
                max_length=30,
            ),
        ),
    ]
