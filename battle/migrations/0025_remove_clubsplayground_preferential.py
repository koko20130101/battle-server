# Generated by Django 4.0 on 2023-12-18 07:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0024_users_honor'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clubsplayground',
            name='preferential',
        ),
    ]
