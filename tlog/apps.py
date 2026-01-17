"""
Конфигурация приложения tlog
"""
from django.apps import AppConfig


class TlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tlog'
    verbose_name = 'TLog приложение'

    def ready(self):
        # Явная загрузка templatetags
        import tlog.templatetags.custom_filters