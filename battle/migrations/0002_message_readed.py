# Generated by Django 4.0 on 2024-01-08 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='readed',
            field=models.BooleanField(default=False),
        ),
    ]
