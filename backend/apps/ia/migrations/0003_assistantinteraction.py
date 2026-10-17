import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("ia", "0002_ianalyse_donnees_entree_ianalyse_recommandation"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("organizations", "0007_alter_organisationrequest_adresse_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="AssistantInteraction",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("conversation_id", models.UUIDField(db_index=True)),
                ("request_text", models.TextField()),
                ("response_text", models.TextField()),
                ("tools_used", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("organization", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="organizations.organization")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
