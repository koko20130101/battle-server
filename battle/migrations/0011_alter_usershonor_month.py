# Generated by Django 4.0 on 2024-06-01 03:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0010_usershonor_month'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usershonor',
            name='month',
            field=models.CharField(default='06', max_length=4),
        ),
    ]