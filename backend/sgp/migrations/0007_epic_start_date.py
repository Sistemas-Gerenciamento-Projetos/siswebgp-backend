# Generated by Django 4.2 on 2023-08-24 16:25

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('sgp', '0006_epic_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='epic',
            name='start_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]