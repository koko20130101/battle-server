# Generated by Django 4.0 on 2024-06-01 03:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0009_rename_mvp_usershonor_assist'),
    ]

    operations = [
        migrations.AddField(
            model_name='usershonor',
            name='month',
            field=models.CharField(default=0, max_length=4),
        ),
    ]