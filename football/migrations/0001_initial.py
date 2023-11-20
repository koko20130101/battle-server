# Generated by Django 4.0 on 2023-11-20 08:53

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
                ('common_name', models.CharField(blank=True, max_length=50)),
                ('avatar', models.URLField(blank=True)),
            ],
            options={
                'db_table': 'fb_users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Clubs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('club_name', models.CharField(max_length=50)),
                ('club_logo', models.TextField(blank=True)),
                ('brief', models.TextField(blank=True)),
                ('honor', models.IntegerField(default=0)),
                ('need_apply', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'fb_clubs',
            },
        ),
        migrations.CreateModel(
            name='GameMembers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('goal', models.IntegerField(default=0)),
                ('group', models.IntegerField(default=0)),
                ('cost', models.FloatField(blank=True)),
            ],
            options={
                'db_table': 'fb_game_members',
            },
        ),
        migrations.CreateModel(
            name='UploadImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('height', models.PositiveIntegerField(default=75)),
                ('width', models.PositiveIntegerField(default=75)),
                ('image_type', models.IntegerField(default=1)),
                ('image_url', models.ImageField(height_field='height', upload_to='upload', width_field='width')),
            ],
            options={
                'db_table': 'fb_upload_imges',
            },
        ),
        migrations.CreateModel(
            name='UsersClubs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.IntegerField(default=3)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='football.clubs')),
                ('use', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='football.users')),
            ],
            options={
                'db_table': 'fb_users_clubs',
            },
        ),
        migrations.CreateModel(
            name='Games',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('start_time', models.DateTimeField(null=True)),
                ('site', models.CharField(max_length=50)),
                ('price', models.FloatField(blank=True)),
                ('original_price', models.FloatField(blank=True)),
                ('cost', models.FloatField(blank=True)),
                ('brief', models.TextField(blank=True)),
                ('group', models.IntegerField(default=1)),
                ('members', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='football.gamemembers')),
            ],
            options={
                'db_table': 'fb_games',
            },
        ),
        migrations.AddField(
            model_name='gamemembers',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='football.games'),
        ),
        migrations.AddField(
            model_name='clubs',
            name='members',
            field=models.ManyToManyField(related_name='users_set', through='football.UsersClubs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Apply',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('applicant_name', models.CharField(blank=True, max_length=15)),
                ('common_name', models.CharField(blank=True, max_length=15)),
                ('club', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='football.clubs')),
            ],
            options={
                'db_table': 'fb_apply',
            },
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.FloatField(blank=True)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='football.clubs')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='football.users')),
            ],
            options={
                'db_table': 'fb_account',
            },
        ),
        migrations.AddField(
            model_name='users',
            name='clubs',
            field=models.ManyToManyField(related_name='clubs_set', through='football.UsersClubs', to='football.Clubs'),
        ),
        migrations.AddField(
            model_name='users',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='users',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
