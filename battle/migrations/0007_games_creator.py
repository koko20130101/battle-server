# Generated by Django 4.0 on 2024-01-21 14:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0006_usershonor_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='games',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='battle.users'),
        ),
    ]
