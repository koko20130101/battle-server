# Generated by Django 4.0 on 2023-12-11 08:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0009_remove_users_clubs'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clubs',
            name='members',
        ),
    ]