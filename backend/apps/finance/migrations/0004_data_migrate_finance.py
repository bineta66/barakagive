from django.db import migrations

def migrate_finance_data(apps, schema_editor):
    Don = apps.get_model('finance', 'Don')
    Donateur = apps.get_model('finance', 'Donateur')
    Depense = apps.get_model('finance', 'Depense')
    
    for don in Don.objects.all():
        bailleur_name = don.bailleur.strip() if don.bailleur else 'Donateur Inconnu'
        if bailleur_name:
            donateur, _ = Donateur.objects.get_or_create(
                nom=bailleur_name,
                organization=don.organization,
                defaults={'type': 'ENTREPRISE'}
            )
            don.donateur = donateur
            don.save()

    for dep in Depense.objects.all():
        if dep.budget and dep.budget.projet:
            dep.projet = dep.budget.projet
            dep.save()

def reverse_finance_data(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0003_budget_devise_depense_devise_depense_projet_and_more'),
    ]

    operations = [
        migrations.RunPython(migrate_finance_data, reverse_finance_data),
    ]
