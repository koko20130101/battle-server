# Generated by Django 4.0 on 2023-12-15 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0020_games_cancel_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='games',
            name='competition',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
