# Generated by Django 4.0 on 2023-12-20 02:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0029_games_site'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='games',
            name='site',
        ),
    ]
