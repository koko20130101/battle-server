# Generated by Django 4.0 on 2023-12-08 01:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='clubs',
            name='short_name',
            field=models.CharField(max_length=8, null=True),
        ),
        migrations.AddField(
            model_name='games',
            name='end_time',
            field=models.TimeField(null=True),
        ),
        migrations.AddField(
            model_name='games',
            name='game_date',
            field=models.TimeField(null=True),
        ),
        migrations.AddField(
            model_name='uploadimages',
            name='club',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='battle.clubs'),
        ),
        migrations.AddField(
            model_name='uploadimages',
            name='game',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='battle.games'),
        ),
        migrations.AddField(
            model_name='uploadimages',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='battle.users'),
        ),
        migrations.AlterField(
            model_name='games',
            name='start_time',
            field=models.TimeField(null=True),
        ),
        migrations.AlterField(
            model_name='uploadimages',
            name='image_url',
            field=models.ImageField(height_field='height', upload_to='battle', verbose_name='封面图', width_field='width'),
        ),
    ]
