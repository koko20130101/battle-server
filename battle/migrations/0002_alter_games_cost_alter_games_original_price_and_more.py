# Generated by Django 4.0 on 2023-12-25 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='games',
            name='cost',
            field=models.FloatField(blank=True, default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='games',
            name='original_price',
            field=models.FloatField(blank=True, default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='games',
            name='price',
            field=models.FloatField(blank=True, default=0),
            preserve_default=False,
        ),
    ]