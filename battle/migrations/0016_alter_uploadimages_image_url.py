# Generated by Django 4.0 on 2023-12-29 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0015_alter_uploadimages_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadimages',
            name='image_url',
            field=models.ImageField(height_field='height', upload_to='upload', width_field='width'),
        ),
    ]
