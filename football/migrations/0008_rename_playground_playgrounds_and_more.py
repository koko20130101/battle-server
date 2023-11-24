# Generated by Django 4.0 on 2023-11-24 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('football', '0007_alter_playground_options_alter_playground_table'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Playground',
            new_name='Playgrounds',
        ),
        migrations.RemoveField(
            model_name='clubs',
            name='playground',
        ),
        migrations.AddField(
            model_name='clubs',
            name='playgrounds',
            field=models.ManyToManyField(related_name='clubs_set', through='football.ClubsPlayground', to='football.Playgrounds'),
        ),
    ]
