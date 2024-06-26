# Generated by Django 4.0 on 2024-01-14 09:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0002_message_readed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='users',
            name='honor',
        ),
        migrations.CreateModel(
            name='UsersHonor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('honor', models.IntegerField(blank=True, default=0)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users_honor_set', to='battle.clubs')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users_honor_set', to='battle.users')),
            ],
            options={
                'db_table': 'bt_users_honor',
            },
        ),
    ]
