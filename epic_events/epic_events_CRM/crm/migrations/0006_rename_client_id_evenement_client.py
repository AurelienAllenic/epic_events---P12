# Generated by Django 5.0.3 on 2024-05-09 17:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0005_evenement_contract'),
    ]

    operations = [
        migrations.RenameField(
            model_name='evenement',
            old_name='client_id',
            new_name='client',
        ),
    ]
