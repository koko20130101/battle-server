# Generated by Django 4.0 on 2023-12-28 10:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0010_battleapply'),
    ]

    operations = [
        migrations.AddField(
            model_name='battleapply',
            name='club',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='battle.clubs'),
        ),
    ]