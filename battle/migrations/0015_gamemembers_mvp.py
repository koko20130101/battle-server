# Generated by Django 4.0 on 2025-01-08 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0014_usershonor_mvp_alter_games_game_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamemembers',
            name='mvp',
            field=models.IntegerField(default=0),
        ),
    ]
