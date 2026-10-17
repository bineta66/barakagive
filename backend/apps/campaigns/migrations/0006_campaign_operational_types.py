from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("campaigns", "0005_campaign_type"),
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
                    ("URGENCE", "Urgence"),
                    ("SENSIBILISATION", "Sensibilisation"),
                    ("SUIVI_EVALUATION", "Suivi et évaluation"),
                ],
                default="DISTRIBUTION",
                max_length=30,
            ),
        ),
    ]
