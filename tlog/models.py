from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


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
    rst_sent = models.CharField(max_length=10, help_text="RST переданный", blank=True, null=True)
    rst_rcvd = models.CharField(max_length=10, help_text="RST принятый", blank=True, null=True)

    # QTH локаторы
    my_gridsquare = models.CharField(max_length=10, help_text="Мой QTH локатор", blank=True, null=True)
    gridsquare = models.CharField(max_length=10, help_text="QTH локатор корреспондента", blank=True, null=True)
    continent = models.CharField(max_length=2, help_text="Континент", blank=True, null=True)

    # Дополнительные поля
    ru_region = models.CharField(max_length=100, help_text="RU область/регион", blank=True, null=True)

    # Дополнительные поля для спутниковой связи и соревнований
    prop_mode = models.CharField(max_length=50, help_text="Режим распространения", blank=True, null=True)
    sat_name = models.CharField(max_length=50, help_text="Название спутника", blank=True, null=True)
    r150s = models.CharField(max_length=100, help_text="R150S", blank=True, null=True)
    dxcc = models.CharField(max_length=10, help_text="DXCC", blank=True, null=True)
    cqz = models.IntegerField(help_text="CQ зона", null=True, blank=True)
    ituz = models.IntegerField(help_text="ITU зона", null=True, blank=True)

    # Подтверждения QSL
    lotw = models.CharField(max_length=1, help_text="Подтверждение LoTW", default='N', blank=True)
    paper_qsl = models.CharField(max_length=1, help_text="Бумажная QSL", default='N', blank=True)

    # Ссылка на загруженный ADIF файл
    adif_upload = models.ForeignKey(
        ADIFUpload,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='qso_records',
        help_text="Связанная загрузка ADIF файла"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-time']
        indexes = [
            # Основные индексы для производительности
            models.Index(fields=['user', '-date', '-time'], name='qso_user_date_time_idx'),
            models.Index(fields=['callsign'], name='qso_callsign_idx'),
            models.Index(fields=['my_callsign'], name='qso_my_callsign_idx'),
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

    # Имя и фамилия (отдельно) - для Django 5.2
    first_name = models.CharField(max_length=100, blank=True, help_text="Имя")
    last_name = models.CharField(max_length=100, blank=True, help_text="Фамилия")

    # QTH
    qth = models.CharField(max_length=100, blank=True, help_text="QTH")

    # Мой QTH локатор
    my_gridsquare = models.CharField(max_length=10, help_text="Мой QTH локатор", blank=True)

    # Позывные (бывшие, действующие, спецпозывные, с дробями) - храним как JSON
    my_callsigns = models.JSONField(default=list, blank=True, help_text="Мои позывные в формате JSON")

    # Блокировка пользователя
    is_blocked = models.BooleanField(default=False, help_text="Заблокировать доступ к личному кабинету")
    blocked_reason = models.TextField(blank=True, help_text="Причина блокировки", default='')
    blocked_at = models.DateTimeField(null=True, blank=True, help_text="Дата блокировки")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Регистрация пользователей'
        verbose_name_plural = 'Регистрация пользователей'

    def __str__(self):
        return f"Profile - {self.user.username} ({self.callsign})"

    def block(self, reason=''):
        """
        Блокирует пользователя
        """
        self.is_blocked = True
        self.blocked_reason = reason
        self.blocked_at = timezone.now()
        self.save()

    def unblock(self):
        """
        Разблокирует пользователя
        """
        self.is_blocked = False
        self.blocked_reason = ''
        self.blocked_at = None
        self.save()

    @property
    def is_user_blocked(self):
        """
        Возвращает True если пользователь заблокирован
        """
        return self.is_blocked

    def save(self, *args, **kwargs):
        """
        Переопределяем save для синхронизации first_name/last_name с User
        """
        # Синхронизируем имя пользователя с полями профиля
        if self.first_name:
            self.user.first_name = self.first_name
        if self.last_name:
            self.user.last_name = self.last_name
        if self.first_name or self.last_name:
            self.user.save(update_fields=['first_name', 'last_name'])
        super().save(*args, **kwargs)


def check_user_blocked(user):
    """
    Проверяет, заблокирован ли пользователь.
    Возвращает (is_blocked, reason) кортеж.
    """
    if not user.is_authenticated:
        return False, ''

    try:
        profile = user.radio_profile
        return profile.is_blocked, profile.blocked_reason or ''
    except RadioProfile.DoesNotExist:
        return False, ''


class ChatMessage(models.Model):
    """
    Сообщения локального чата между пользователями
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    username = models.CharField(max_length=150, help_text="Имя пользователя (callsign)")
    message = models.TextField(help_text="Текст сообщения")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Сообщение чата'
        verbose_name_plural = 'Сообщения чата'

    def __str__(self):
        return f"{self.username}: {self.message[:50]}..."