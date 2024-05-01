# Generated by Django 5.0.3 on 2024-04-29 13:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_name', models.CharField(max_length=100)),
                ('client_contact', models.CharField(max_length=100)),
                ('day_start', models.DateField()),
                ('date_end', models.DateField()),
                ('location', models.CharField(max_length=100)),
                ('attendees', models.PositiveIntegerField()),
                ('notes', models.TextField()),
                ('client_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.client')),
                ('support_contact', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='Evenement',
        ),
    ]