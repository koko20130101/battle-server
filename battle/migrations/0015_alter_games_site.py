# Generated by Django 4.0 on 2023-12-14 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0014_alter_games_end_time_alter_games_site_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='games',
            name='site',
            field=models.CharField(blank=True, default='', max_length=50, null=True),
        ),
    ]
