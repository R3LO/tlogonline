# Generated manually for Cosmos diploma optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tlog', '0029_auto_20260205_1746'),
    ]

    operations = [
        # Удаляем старые индексы (если они есть)
        migrations.RemoveIndex(
            model_name='qso',
            name='qso_user_date_time_idx',
        ),
        migrations.RemoveIndex(
            model_name='qso',
            name='qso_callsign_idx',
        ),
        migrations.RemoveIndex(
            model_name='qso',
            name='qso_my_callsign_idx',
        ),
        migrations.RemoveIndex(
            model_name='qso',
            name='qso_mode_idx',
        ),
        migrations.RemoveIndex(
            model_name='qso',
            name='qso_band_idx',
        ),
        migrations.RemoveIndex(
            model_name='qso',
            name='qso_date_time_idx',
        ),
        migrations.RemoveIndex(
            model_name='qso',
            name='qso_unique_constraint_idx',
        ),
        # Добавляем обновленные индексы с оптимизацией для Cosmos
        migrations.AddIndex(
            model_name='qso',
            index=models.Index(fields=['user', '-date', '-time'], name='qso_user_date_time_idx'),
        ),
        migrations.AddIndex(
            model_name='qso',
            index=models.Index(fields=['callsign'], name='qso_callsign_idx'),
        ),
        migrations.AddIndex(
            model_name='qso',
            index=models.Index(fields=['my_callsign'], name='qso_my_callsign_idx'),
        ),
        migrations.AddIndex(
            model_name='qso',
            index=models.Index(fields=['mode'], name='qso_mode_idx'),
        ),
        migrations.AddIndex(
            model_name='qso',
            index=models.Index(fields=['band'], name='qso_band_idx'),
        ),
        migrations.AddIndex(
            model_name='qso',
            index=models.Index(fields=['date', 'time'], name='qso_date_time_idx'),
        ),
        # Новые индексы для оптимизации запросов Cosmos и спутниковой связи
        migrations.AddIndex(
            model_name='qso',
            index=models.Index(fields=['prop_mode'], name='qso_prop_mode_idx'),
        ),
        migrations.AddIndex(
            model_name='qso',
            index=models.Index(fields=['gridsquare'], name='qso_gridsquare_idx'),
        ),
        # Составной индекс для оптимизации поиска спутниковых QSO
        migrations.AddIndex(
            model_name='qso',
            index=models.Index(fields=['user', 'my_callsign', 'prop_mode', 'band'], name='qso_cosmos_satellite_idx'),
        ),
        # Составной индекс для предотвращения дублирования
        migrations.AddIndex(
            model_name='qso',
            index=models.Index(
                fields=['user', 'my_callsign', 'callsign', 'date', 'time', 'band', 'mode'],
                name='qso_unique_constraint_idx'
            ),
        ),
    ]
