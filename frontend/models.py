from django.db import models
from django.contrib.auth.models import User
import uuid


class QSO(models.Model):
    """
    Модель для хранения записей радиосвязей
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='qsos')

    # Дата и время связи (отдельные поля для оптимизации)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)

    # Позывные
    my_callsign = models.CharField(max_length=20, help_text="Мой позывной", default='')
    callsign = models.CharField(max_length=20, help_text="Позывной корреспондента")

    # Техническая информация
    frequency = models.FloatField(help_text="Частота в МГц", null=True, blank=True)
    band = models.CharField(
        max_length=10,
        help_text="Диапазон",
        null=True,
        blank=True
    )
    mode = models.CharField(
        max_length=20,
        choices=[
            ('SSB', 'SSB'),
            ('CW', 'CW'),
            ('FM', 'FM'),
            ('AM', 'AM'),
            ('RTTY', 'RTTY'),
            ('PSK31', 'PSK31'),
            ('PSK63', 'PSK63'),
            ('FT8', 'FT8'),
            ('FT4', 'FT4'),
            ('JT65', 'JT65'),
            ('JT9', 'JT9'),
            ('SSTV', 'SSTV'),
            ('JS8', 'JS8'),
            ('MSK144', 'MSK144'),
        ]
    )

    # RST сигналы
    rst_sent = models.CharField(max_length=10, help_text="RST переданный", blank=True)
    rst_received = models.CharField(max_length=10, help_text="RST принятый", blank=True)

    # QTH локаторы
    my_gridsquare = models.CharField(max_length=10, help_text="Мой QTH локатор", blank=True)
    his_gridsquare = models.CharField(max_length=10, help_text="QTH локатор корреспондента", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-time']
        indexes = [
            # Основные индексы для производительности
            models.Index(fields=['user', '-date', '-time'], name='qso_user_date_time_idx'),
            models.Index(fields=['callsign'], name='qso_callsign_idx'),
            models.Index(fields=['mode'], name='qso_mode_idx'),
            models.Index(fields=['band'], name='qso_band_idx'),
            models.Index(fields=['date', 'time'], name='qso_date_time_idx'),
            # Составной индекс для предотвращения дублирования
            models.Index(
                fields=['user', 'my_callsign', 'callsign', 'date', 'time', 'band', 'mode'],
                name='qso_unique_constraint_idx'
            ),
        ]
        # Уникальные ограничения для предотвращения дублирования
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'my_callsign', 'callsign', 'date', 'time', 'band', 'mode'],
                name='unique_qso'
            )
        ]

    def __str__(self):
        date_str = self.date.strftime('%Y-%m-%d') if self.date else 'N/A'
        time_str = self.time.strftime('%H:%M') if self.time else 'N/A'
        return f"{self.my_callsign} -> {self.callsign} ({self.band}) - {date_str} {time_str}"


class RadioProfile(models.Model):
    """
    Профиль радиолюбителя
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='radio_profile')
    callsign = models.CharField(max_length=20, blank=True)
    full_name = models.CharField(max_length=100, blank=True, help_text="Полное имя")
    qth = models.CharField(max_length=100, blank=True, help_text="QTH")
    license_class = models.CharField(max_length=10, blank=True, help_text="Класс лицензии")

    # Антенна
    antenna_type = models.CharField(max_length=100, blank=True)
    antenna_height = models.CharField(max_length=50, blank=True)

    # Радиостанция
    radio_model = models.CharField(max_length=100, blank=True)
    power_output = models.CharField(max_length=20, blank=True)

    # Мой QTH локатор
    my_gridsquare = models.CharField(max_length=10, help_text="Мой QTH локатор", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile - {self.user.username} ({self.callsign})"


class ADIFUpload(models.Model):
    """
    Загруженные ADIF файлы
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adif_uploads')
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    upload_date = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    qso_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)

    def __str__(self):
        return f"{self.file_name} - {self.user.username}"