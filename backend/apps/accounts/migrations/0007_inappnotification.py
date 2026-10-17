import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0006_add_invited_status"),
        ("organizations", "0007_alter_organisationrequest_adresse_and_more"),
        ("projects", "0006_remove_project_budget"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="InAppNotification",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=180)),
                ("message", models.TextField(max_length=2000)),
                ("source", models.CharField(default="ASSISTANT", max_length=40)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("read_at", models.DateTimeField(blank=True, null=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_in_app_notifications", to=settings.AUTH_USER_MODEL)),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to="organizations.organization")),
                ("project", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assistant_notifications", to="projects.project")),
                ("recipient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="in_app_notifications", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="inappnotification",
            index=models.Index(fields=["recipient", "read_at", "created_at"], name="acct_notif_r_created_idx"),
        ),
    ]
