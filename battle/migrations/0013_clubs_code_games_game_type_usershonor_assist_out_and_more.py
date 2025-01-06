# Generated by Django 4.0 on 2025-01-05 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0012_usersclubs_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='clubs',
            name='code',
            field=models.CharField(max_length=24, null=True),
        ),
        migrations.AddField(
            model_name='games',
            name='game_type',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='usershonor',
            name='assist_out',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='usershonor',
            name='goal_out',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='usershonor',
            name='month',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='usershonor',
            name='year',
            field=models.CharField(default='2025', max_length=4),
        ),
    ]
