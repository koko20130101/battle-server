# Generated by Django 4.0 on 2023-12-29 07:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0014_advert_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadimages',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='battle.users'),
        ),
    ]
