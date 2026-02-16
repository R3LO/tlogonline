"""
Модуль для работы с настройками пользователя
Настройки сохраняются в JSON файл в домашней директории пользователя
"""
import json
import os
from pathlib import Path


class Settings:
    """Класс для управления настройками приложения"""

    def __init__(self):
        # Определяем путь к файлу настроек
        self.config_dir = Path.home() / '.tlog_rest_client'
        self.config_file = self.config_dir / 'settings.json'

        # Создаем директорию, если она не существует
        self.config_dir.mkdir(exist_ok=True)

        # Загружаем настройки
        self.settings = self._load_settings()

    def _load_settings(self):
        """Загружает настройки из файла"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        # Настройки по умолчанию
        return {
            'api_url': 'http://127.0.0.1:8000',
            'username': '',
            'password': '',
            'remember_credentials': False,
            'window_geometry': None,
            'window_state': None,
            'table_column_widths': {},
            'last_search_type': 'callsign',  # 'callsign' или 'grid'
        }

    def save(self):
        """Сохраняет настройки в файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Ошибка сохранения настроек: {e}")

    def get(self, key, default=None):
        """Получает значение настройки"""
        return self.settings.get(key, default)

    def set(self, key, value):
        """Устанавливает значение настройки"""
        self.settings[key] = value
        self.save()

    def get_api_url(self):
        """Возвращает URL API"""
        return self.settings.get('api_url', 'http://127.0.0.1:8000')

    def set_api_url(self, url):
        """Устанавливает URL API"""
        self.settings['api_url'] = url.rstrip('/')
        self.save()

    def get_credentials(self):
        """Возвращает учетные данные пользователя"""
        if self.settings.get('remember_credentials', False):
            return self.settings.get('username', ''), self.settings.get('password', '')
        return '', ''

    def set_credentials(self, username, password, remember=False):
        """Устанавливает учетные данные"""
        self.settings['username'] = username
        if remember:
            self.settings['password'] = password
        else:
            self.settings['password'] = ''
        self.settings['remember_credentials'] = remember
        self.save()

    def clear_credentials(self):
        """Очищает сохраненные учетные данные"""
        self.settings['username'] = ''
        self.settings['password'] = ''
        self.settings['remember_credentials'] = False
        self.save()
