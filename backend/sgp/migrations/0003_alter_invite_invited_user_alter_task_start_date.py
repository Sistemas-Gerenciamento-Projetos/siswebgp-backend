# Generated by Django 4.2 on 2023-05-28 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sgp', '0002_remove_invite_user_invited_invite_invited_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invite',
            name='invited_user',
            field=models.EmailField(default=2, max_length=254),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='task',
            name='start_date',
            field=models.DateTimeField(),
        ),
    ]
