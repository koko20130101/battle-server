# Generated by Django 4.0 on 2024-01-08 02:30

import common.utils
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('open_id', models.CharField(max_length=100)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('real_name', models.CharField(blank=True, max_length=15)),
                ('nick_name', models.CharField(blank=True, max_length=50)),
                ('avatar', models.URLField(blank=True)),
                ('honor', models.IntegerField(blank=True, default=0)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'bt_users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Advert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=30)),
                ('status', models.BooleanField(default=False)),
                ('row', models.IntegerField(default=1)),
                ('ad_pic', models.TextField(blank=True)),
                ('ad_pic_height', models.IntegerField(default=0)),
                ('ad_type', models.IntegerField(default=0)),
                ('jump_type', models.IntegerField(default=0)),
                ('jump_url', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'bt_advert',
            },
        ),
        migrations.CreateModel(
            name='Clubs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('club_name', models.CharField(max_length=50)),
                ('short_name', models.CharField(max_length=8, null=True)),
                ('club_logo', models.TextField(blank=True)),
                ('area', models.CharField(max_length=50, null=True)),
                ('area_code', models.CharField(max_length=50, null=True)),
                ('club_type', models.IntegerField(default=1)),
                ('brief', models.TextField(blank=True)),
                ('sort', models.IntegerField(default=0)),
                ('honor', models.IntegerField(default=0)),
                ('credit', models.IntegerField(default=0)),
                ('game_total', models.IntegerField(default=0)),
                ('need_apply', models.BooleanField(default=True)),
                ('hot', models.BooleanField(default=False)),
                ('main_playground', models.CharField(blank=True, default='', max_length=50)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='clubs_set1', to='battle.users')),
            ],
            options={
                'db_table': 'bt_clubs',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Playgrounds',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('playground_name', models.CharField(max_length=30)),
                ('play_type', models.IntegerField(default=1)),
                ('area', models.CharField(max_length=50, null=True)),
                ('area_code', models.CharField(max_length=50, null=True)),
                ('address', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'bt_playground',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='UsersClubs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.IntegerField(default=3)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users_clubs_set', to='battle.clubs')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users_clubs_set', to='battle.users')),
            ],
            options={
                'db_table': 'bt_users_clubs',
            },
        ),
        migrations.CreateModel(
            name='UploadImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('height', models.PositiveIntegerField(default=155)),
                ('width', models.PositiveIntegerField(default=155)),
                ('image_type', models.IntegerField(default=0)),
                ('image_url', models.ImageField(height_field='height', upload_to=common.utils.get_upload_to, width_field='width')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='battle.users')),
            ],
            options={
                'db_table': 'bt_upload_imges',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(blank=True)),
                ('m_type', models.IntegerField(default=1)),
                ('reply', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('reply_time', models.DateTimeField(null=True)),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='battle.users')),
            ],
            options={
                'db_table': 'bt_messages',
            },
        ),
        migrations.CreateModel(
            name='Games',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=50, null=True)),
                ('tag', models.CharField(blank=True, max_length=10, null=True)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('min_people', models.IntegerField(blank=True, default=0, null=True)),
                ('max_people', models.IntegerField(blank=True, default=0, null=True)),
                ('competition', models.IntegerField(blank=True, default=0, null=True)),
                ('cancel_time', models.IntegerField(blank=True, default=0, null=True)),
                ('open_battle', models.BooleanField(default=False)),
                ('price', models.FloatField(blank=True)),
                ('original_price', models.FloatField(blank=True)),
                ('cost', models.FloatField(blank=True)),
                ('status', models.IntegerField(default=0)),
                ('brief', models.TextField(blank=True)),
                ('group', models.IntegerField(default=1)),
                ('remarks', models.CharField(blank=True, max_length=50, null=True)),
                ('battle', models.OneToOneField(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='battle.games')),
                ('club', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='battle.clubs')),
                ('playground', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='battle.playgrounds')),
            ],
            options={
                'db_table': 'bt_games',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='GameMembers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remarks', models.CharField(blank=True, max_length=30, null=True)),
                ('goal', models.IntegerField(default=0)),
                ('group', models.IntegerField(default=0)),
                ('cost', models.CharField(blank=True, max_length=50, null=True)),
                ('free', models.BooleanField(default=False)),
                ('club', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='battle.clubs')),
                ('game', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='battle.games')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='battle.users')),
            ],
            options={
                'db_table': 'bt_game_members',
            },
        ),
        migrations.CreateModel(
            name='ClubsPlaygrounds',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('main', models.BooleanField(default=False)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clubs_playground_set', to='battle.clubs')),
                ('playground', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clubs_playground_set', to='battle.playgrounds')),
            ],
            options={
                'db_table': 'bt_clubs_playgrounds',
            },
        ),
        migrations.AddField(
            model_name='clubs',
            name='members',
            field=models.ManyToManyField(related_name='clubs_set', through='battle.UsersClubs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='clubs',
            name='playgrounds',
            field=models.ManyToManyField(related_name='clubs_set', through='battle.ClubsPlaygrounds', to='battle.Playgrounds'),
        ),
        migrations.CreateModel(
            name='ClubAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.FloatField(blank=True)),
                ('account_type', models.IntegerField(blank=True, default=1)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='battle.clubs')),
                ('playground', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='battle.playgrounds')),
            ],
            options={
                'db_table': 'bt_club_account',
            },
        ),
        migrations.CreateModel(
            name='BattleApply',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('remarks', models.TextField(max_length=50, null=True)),
                ('game', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='game_set1', to='battle.games')),
                ('rival', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='game_set2', to='battle.games')),
            ],
            options={
                'db_table': 'bt_battle_apply',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Apply',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('remarks', models.TextField(max_length=50, null=True)),
                ('apply_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='battle.users')),
                ('club', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='battle.clubs')),
            ],
            options={
                'db_table': 'bt_apply',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='AccountRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(blank=True)),
                ('amount_type', models.IntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='battle.clubs')),
                ('game', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='battle.games')),
                ('playground', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='battle.playgrounds')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='battle.users')),
            ],
            options={
                'db_table': 'bt_account_record',
            },
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.FloatField(blank=True)),
                ('account_type', models.IntegerField(blank=True, default=1)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='battle.clubs')),
                ('playground', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='battle.playgrounds')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='battle.users')),
            ],
            options={
                'db_table': 'bt_account',
            },
        ),
    ]
