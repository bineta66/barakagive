# Generated manually for OrganisationRequest & AIVerificationReport

import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0004_alter_subscription_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganisationRequest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nom_ong', models.CharField(max_length=255, verbose_name="Nom de l'ONG")),
                ('sigle', models.CharField(blank=True, max_length=50, verbose_name='Sigle / Acronyme')),
                ('domaine', models.CharField(blank=True, max_length=150, verbose_name="Domaine d'intervention")),
                ('region', models.CharField(blank=True, max_length=100, verbose_name='Région')),
                ('adresse', models.TextField(blank=True, verbose_name='Adresse du siège')),
                ('gerant_nom', models.CharField(max_length=150, verbose_name='Nom du gérant')),
                ('gerant_prenom', models.CharField(max_length=150, verbose_name='Prénom du gérant')),
                ('gerant_email', models.EmailField(max_length=254, verbose_name='Email du gérant')),
                ('gerant_telephone', models.CharField(max_length=50, verbose_name='Téléphone du gérant')),
                ('recepisse_pdf', models.FileField(upload_to='organisation_requests/recepisse/', verbose_name='Récépissé (PDF)')),
                ('ninea_pdf', models.FileField(upload_to='organisation_requests/ninea/', verbose_name='NINEA (PDF)')),
                ('statuts_pdf', models.FileField(upload_to='organisation_requests/statuts/', verbose_name='Statuts (PDF)')),
                ('statut', models.CharField(choices=[('EN_ATTENTE', 'En attente'), ('APPROUVEE', 'Approuvée'), ('REJETEE', 'Rejetée')], default='EN_ATTENTE', max_length=20)),
                ('ai_report', models.JSONField(blank=True, default=dict, verbose_name='Rapport IA')),
                ('motif_rejet', models.TextField(blank=True, verbose_name='Motif de rejet')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('organization', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='requests', to='organizations.organization')),
            ],
            options={
                'verbose_name': "Demande d'inscription ONG",
                'verbose_name_plural': "Demandes d'inscription ONG",
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AIVerificationReport',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('score_confiance', models.IntegerField(default=0, verbose_name='Score de confiance (%)')),
                ('statut_ia', models.CharField(choices=[('A_VERIFIER', 'À vérifier'), ('CONFORME', 'Conforme'), ('NON_CONFORME', 'Non conforme')], default='A_VERIFIER', max_length=20)),
                ('nom_extrait', models.CharField(blank=True, max_length=255, verbose_name='Nom extrait (OCR)')),
                ('ninea_extrait', models.CharField(blank=True, max_length=100, verbose_name='NINEA extrait')),
                ('recepisse_extrait', models.CharField(blank=True, max_length=100, verbose_name='N° récépissé extrait')),
                ('documents', models.JSONField(default=list, verbose_name='État des documents')),
                ('observation', models.TextField(blank=True, verbose_name='Observation IA')),
                ('recommandation', models.TextField(blank=True, verbose_name='Recommandation')),
                ('anomalies', models.JSONField(default=list, verbose_name='Anomalies détectées')),
                ('raw_response', models.JSONField(default=dict, verbose_name='Réponse brute IA')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='verification_report', to='organizations.organisationrequest')),
            ],
            options={
                'verbose_name': 'Rapport de vérification IA',
                'verbose_name_plural': 'Rapports de vérification IA',
            },
        ),
    ]
