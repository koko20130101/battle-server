# Generated by Django 4.0 on 2024-01-21 17:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0008_remove_gamemembers_mvp_gamemembers_assist'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usershonor',
            old_name='mvp',
            new_name='assist',
        ),
    ]
