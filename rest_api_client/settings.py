"""
Модуль для работы с настройками пользователя
Настройки сохраняются в INI файл в домашней директории пользователя
"""
from PySide6.QtCore import QSettings
from pathlib import Path


class Settings:
    """Класс для управления настройками приложения"""

    def __init__(self):
        # Определяем путь к файлу настроек в текущей директории
        self.config_file = Path.cwd() / 'settings.ini'

        # Инициализируем QSettings с форматом INI
        self.settings = QSettings(str(self.config_file), QSettings.IniFormat)

    def get(self, key, default=None):
        """Получает значение настройки"""
        return self.settings.value(key, default)

    def set(self, key, value):
        """Устанавливает значение настройки"""
        self.settings.setValue(key, value)
        self.settings.sync()

    def get_api_url(self):
        """Возвращает URL API"""
        return self.settings.value('api_url', 'http://127.0.0.1:8000')

    def set_api_url(self, url):
        """Устанавливает URL API"""
        self.settings.setValue('api_url', url.rstrip('/'))
        self.settings.sync()

    def get_credentials(self):
        """Возвращает учетные данные пользователя"""
        username = self.settings.value('username', '')
        password = self.settings.value('password', '')
        return username, password

    def set_credentials(self, username, password, remember=True):
        """Устанавливает учетные данные"""
        self.settings.setValue('username', username)
        self.settings.setValue('password', password)
        self.settings.setValue('remember_credentials', remember)
        self.settings.sync()

    def clear_credentials(self):
        """Очищает сохраненные учетные данные"""
        self.settings.setValue('username', '')
        self.settings.setValue('password', '')
        self.settings.setValue('remember_credentials', False)
        self.settings.sync()

    def get_window_geometry(self):
        """Возвращает геометрию окна"""
        return self.settings.value('window_geometry')

    def set_window_geometry(self, geometry):
        """Устанавливает геометрию окна"""
        self.settings.setValue('window_geometry', geometry)
        self.settings.sync()

    def get_window_state(self):
        """Возвращает состояние окна"""
        return self.settings.value('window_state')

    def set_window_state(self, state):
        """Устанавливает состояние окна"""
        self.settings.setValue('window_state', state)
        self.settings.sync()

    def get_table_column_widths(self, table_name):
        """Возвращает ширину колонок таблицы"""
        return self.settings.value(f'table/{table_name}/column_widths', {})

    def set_table_column_widths(self, table_name, widths):
        """Устанавливает ширину колонок таблицы"""
        self.settings.setValue(f'table/{table_name}/column_widths', widths)
        self.settings.sync()

    def get_table_column_order(self, table_name):
        """Возвращает порядок колонок таблицы"""
        return self.settings.value(f'table/{table_name}/column_order', {})

    def set_table_column_order(self, table_name, order):
        """Устанавливает порядок колонок таблицы"""
        self.settings.setValue(f'table/{table_name}/column_order', order)
        self.settings.sync()

    def get_table_sort_column(self, table_name):
        """Возвращает колонку сортировки таблицы"""
        return self.settings.value(f'table/{table_name}/sort_column', -1)

    def set_table_sort_column(self, table_name, column):
        """Устанавливает колонку сортировки таблицы"""
        self.settings.setValue(f'table/{table_name}/sort_column', column)
        self.settings.sync()

    def get_table_sort_order(self, table_name):
        """Возвращает порядок сортировки таблицы"""
        return self.settings.value(f'table/{table_name}/sort_order', 0)

    def set_table_sort_order(self, table_name, order):
        """Устанавливает порядок сортировки таблицы"""
        self.settings.setValue(f'table/{table_name}/sort_order', order)
        self.settings.sync()
