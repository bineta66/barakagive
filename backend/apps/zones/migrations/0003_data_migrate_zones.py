from django.db import migrations
from django.contrib.gis.geos import GEOSGeometry

def migrate_zones_data(apps, schema_editor):
    Zone = apps.get_model('zones', 'Zone')
    Region = apps.get_model('zones', 'Region')
    Department = apps.get_model('zones', 'Department')
    
    poly = GEOSGeometry('POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))')
    
    for z in Zone.objects.all():
        reg_name = z.region.strip() if z.region else 'Dakar'
        r = Region.objects.filter(nom__iexact=reg_name).first()
        if not r:
            r = Region.objects.create(nom=reg_name, geometrie=poly)
        
        dept_nom = z.departement.strip() if z.departement else r.nom
        d = Department.objects.filter(nom__iexact=dept_nom, region=r).first()
        if not d:
            d = Department.objects.create(nom=dept_nom, region=r, geometrie=poly)
        
        z.region_fk = r
        z.departement_fk = d
        z.save()

def reverse_zones_data(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('zones', '0002_zone_departement_fk_zone_region_fk'),
    ]

    operations = [
        migrations.RunPython(migrate_zones_data, reverse_zones_data),
    ]
