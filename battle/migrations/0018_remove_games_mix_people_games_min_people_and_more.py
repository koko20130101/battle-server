# Generated by Django 4.0 on 2023-12-14 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0017_alter_games_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='games',
            name='mix_people',
        ),
        migrations.AddField(
            model_name='games',
            name='min_people',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='games',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='games',
            name='max_people',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='games',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='games',
            name='title',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]