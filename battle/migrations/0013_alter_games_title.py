# Generated by Django 4.0 on 2023-12-13 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0012_remove_games_game_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='games',
            name='title',
            field=models.CharField(max_length=50, null=True),
        ),
    ]