# Generated for adding email and telephone to OrganisationRequest

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0005_organisationrequest_aiverificationreport'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisationrequest',
            name='email',
            field=models.EmailField(default='contact@ong.org', max_length=254, verbose_name='Email de contact'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='organisationrequest',
            name='telephone',
            field=models.CharField(default='+221000000000', max_length=30, verbose_name='Téléphone'),
            preserve_default=False,
        ),
    ]
