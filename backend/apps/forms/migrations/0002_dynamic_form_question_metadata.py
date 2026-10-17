import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("forms", "0001_initial"),
        ("projects", "0006_remove_project_budget"),
    ]

    operations = [
        migrations.AddField(
            model_name="formfield",
            name="critere",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="form_fields", to="projects.projectcriteria"),
        ),
        migrations.AddField(
            model_name="formfield",
            name="source",
            field=models.CharField(choices=[("IA", "IA"), ("MANUEL", "Manuel")], default="MANUEL", max_length=10),
        ),
        migrations.AddField(
            model_name="formfield",
            name="aide",
            field=models.CharField(blank=True, default="", max_length=500),
        ),
        migrations.AlterField(
            model_name="formfield",
            name="type",
            field=models.CharField(choices=[("TEXT", "Texte court"), ("EMAIL", "Email"), ("PHONE", "Téléphone"), ("SELECT", "Liste déroulante"), ("RADIO", "Choix unique"), ("CHECKBOX", "Cases à cocher"), ("YES_NO", "Oui/Non"), ("GPS", "Coordonnées GPS"), ("NUMBER", "Nombre"), ("DATE", "Date"), ("TEXTAREA", "Texte long"), ("PHOTO", "Photo"), ("FILE", "Fichier"), ("SCALE", "Échelle de 1 à 5")], max_length=20),
        ),
    ]
