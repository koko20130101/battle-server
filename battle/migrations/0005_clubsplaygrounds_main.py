# Generated by Django 4.0 on 2023-12-26 01:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0004_remove_clubs_captain_clubs_club_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='clubsplaygrounds',
            name='main',
            field=models.BooleanField(default=False),
        ),
    ]
