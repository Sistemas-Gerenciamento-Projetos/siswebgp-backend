# Generated by Django 4.2 on 2023-08-19 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sgp', '0003_alter_invite_invited_user_alter_task_start_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='number',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]