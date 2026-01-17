# Generated migration for QSO model update

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128)),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ADIFUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=255)),
                ('file_size', models.IntegerField()),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
                ('processed', models.BooleanField(default=False)),
                ('qso_count', models.IntegerField(default=0)),
                ('error_message', models.TextField(blank=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='adif_uploads', to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='QSO',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('date', models.DateField(blank=True, null=True)),
                ('time', models.TimeField(blank=True, null=True)),
                ('my_callsign', models.CharField(default='', help_text='Мой позывной', max_length=20)),
                ('callsign', models.CharField(help_text='Позывной корреспондента', max_length=20)),
                ('frequency', models.FloatField(blank=True, help_text='Частота в МГц', null=True)),
                ('band', models.CharField(blank=True, help_text='Диапазон', max_length=10, null=True)),
                ('mode', models.CharField(choices=[('SSB', 'SSB'), ('CW', 'CW'), ('FM', 'FM'), ('AM', 'AM'), ('RTTY', 'RTTY'), ('PSK31', 'PSK31'), ('PSK63', 'PSK63'), ('FT8', 'FT8'), ('FT4', 'FT4'), ('JT65', 'JT65'), ('JT9', 'JT9'), ('SSTV', 'SSTV'), ('JS8', 'JS8'), ('MSK144', 'MSK144')], max_length=20)),
                ('rst_sent', models.CharField(blank=True, help_text='RST переданный', max_length=10)),
                ('rst_received', models.CharField(blank=True, help_text='RST принятый', max_length=10)),
                ('my_gridsquare', models.CharField(blank=True, help_text='Мой QTH локатор', max_length=10)),
                ('his_gridsquare', models.CharField(blank=True, help_text='QTH локатор корреспондента', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='qsos', to='auth.user')),
            ],
            options={
                'ordering': ['-date', '-time'],
                'indexes': [
                    models.Index(fields=['user', '-date', '-time'], name='qso_user_date_time_idx'),
                    models.Index(fields=['callsign'], name='qso_callsign_idx'),
                    models.Index(fields=['mode'], name='qso_mode_idx'),
                    models.Index(fields=['band'], name='qso_band_idx'),
                    models.Index(fields=['date', 'time'], name='qso_date_time_idx'),
                    models.Index(fields=['user', 'my_callsign', 'callsign', 'date', 'time', 'band', 'mode'], name='qso_unique_constraint_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='RadioProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('callsign', models.CharField(blank=True, help_text='Позывной', max_length=20)),
                ('full_name', models.CharField(blank=True, help_text='Полное имя', max_length=100)),
                ('qth', models.CharField(blank=True, help_text='QTH', max_length=100)),
                ('license_class', models.CharField(blank=True, help_text='Класс лицензии', max_length=10)),
                ('antenna_type', models.CharField(blank=True, help_text='Тип антенны', max_length=100)),
                ('antenna_height', models.CharField(blank=True, help_text='Высота антенны', max_length=50)),
                ('radio_model', models.CharField(blank=True, help_text='Модель радиостанции', max_length=100)),
                ('power_output', models.CharField(blank=True, help_text='Выходная мощность', max_length=20)),
                ('my_gridsquare', models.CharField(blank=True, help_text='Мой QTH локатор', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='radio_profile', to='auth.user')),
            ],
        ),
        migrations.AddConstraint(
            model_name='qso',
            constraint=models.UniqueConstraint(fields=['user', 'my_callsign', 'callsign', 'date', 'time', 'band', 'mode'], name='unique_qso'),
        ),
    ]