# Generated by Django 4.0 on 2023-12-08 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0004_alter_uploadimages_image_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uploadimages',
            name='club',
        ),
        migrations.RemoveField(
            model_name='uploadimages',
            name='game',
        ),
        migrations.AlterField(
            model_name='uploadimages',
            name='image_url',
            field=models.ImageField(height_field='height', upload_to='battle', width_field='width'),
        ),
    ]
