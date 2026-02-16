"""
Главное окно приложения
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget, QStatusBar,
    QMessageBox, QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
    QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

from rest_api_client.api_client import APIClient
from rest_api_client.settings import Settings
from rest_api_client.tabs import SearchTab, StatsTab, ProfileTab
from rest_api_client.tables import populate_compact_table
from rest_api_client.workers import WorkerThread


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.api_client = APIClient(self.settings.get_api_url())
        self.current_worker = None

        self.setup_ui()
        self.setup_connections()
        self.load_settings()
        self.auto_connect()

    def setup_ui(self):
        """Настраивает интерфейс"""
        self.setWindowTitle("TLog Search")
        self.setMinimumSize(700, 500)
        self.resize(800, 600)

        # Меню
        self.create_menu()

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Вкладки
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.on_tab_changed)
        main_layout.addWidget(self.tabs)

        # Создаем вкладки
        self.search_tab = SearchTab()
        self.stats_tab = StatsTab()
        self.profile_tab = ProfileTab()

        self.tabs.addTab(self.search_tab, "Поиск")
        self.tabs.addTab(self.stats_tab, "Статистика")
        self.tabs.addTab(self.profile_tab, "Профиль")

        # Поиск - первая вкладка по умолчанию
        self.tabs.setCurrentWidget(self.search_tab)

        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_connection_status(False)

    def setup_connections(self):
        """Настраивает сигналы и слоты"""
        # Поиск
        self.search_tab.search_btn.clicked.connect(self.perform_search)
        self.search_tab.search_input.returnPressed.connect(self.perform_search)
        self.search_tab.clear_search_btn.clicked.connect(self.clear_search)

        # Статистика
        self.stats_tab.refresh_stats_btn.clicked.connect(self.load_stats)

        # Профиль
        self.profile_tab.refresh_profile_btn.clicked.connect(self.load_profile)

    def create_menu(self):
        """Создает меню приложения"""
        menubar = self.menuBar()

        # Меню Файл
        file_menu = menubar.addMenu("Файл")

        connect_action = QAction("Подключиться...", self)
        connect_action.setShortcut("Ctrl+K")
        connect_action.triggered.connect(self.show_connection_dialog)
        file_menu.addAction(connect_action)

        disconnect_action = QAction("Отключиться", self)
        disconnect_action.setShortcut("Ctrl+D")
        disconnect_action.triggered.connect(self.disconnect_from_server)
        file_menu.addAction(disconnect_action)

        file_menu.addSeparator()

        remember_action = QAction("Запомнить учетные данные", self)
        remember_action.setCheckable(True)
        remember_action.setChecked(self.settings.get('remember_credentials', False))
        remember_action.triggered.connect(self.toggle_remember_credentials)
        file_menu.addAction(remember_action)

        file_menu.addSeparator()

        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню Настройки
        settings_menu = menubar.addMenu("Настройки")

        clear_creds_action = QAction("Очистить сохраненные пароли", self)
        clear_creds_action.triggered.connect(self.clear_credentials)
        settings_menu.addAction(clear_creds_action)

        # Меню Справка
        help_menu = menubar.addMenu("Справка")

        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def load_settings(self):
        """Загружает сохраненные настройки"""
        last_search_type = self.settings.get('last_search_type', 'callsign')
        self.search_tab.search_type_combo.setCurrentIndex({
            'callsign': 0, 'grid': 1, 'band': 2
        }.get(last_search_type, 0))

        # Восстанавливаем размер окна
        width = self.settings.get('window_width', 800)
        height = self.settings.get('window_height', 600)
        self.resize(width, height)

    def auto_connect(self):
        """Автоматическое подключение при запуске"""
        if self.settings.get('remember_credentials', False):
            username, password = self.settings.get_credentials()
            if username and password:
                url = self.settings.get_api_url()
                self.api_client = APIClient(url)
                self.api_client.set_credentials(username, password)
                self.connect_to_server(show_dialog=False)

    def show_connection_dialog(self):
        """Показывает диалог подключения"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Подключение к серверу")
        dialog.setMinimumWidth(400)

        layout = QFormLayout(dialog)

        url_input = QLineEdit()
        url_input.setText(self.settings.get_api_url())
        url_input.setPlaceholderText("http://127.0.0.1:8000")
        layout.addRow("URL сервера:", url_input)

        username_input = QLineEdit()
        username, password = self.settings.get_credentials()
        username_input.setText(username)
        username_input.setPlaceholderText("Имя пользователя")
        layout.addRow("Пользователь:", username_input)

        password_input = QLineEdit()
        password_input.setText(password)
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setPlaceholderText("Пароль")
        layout.addRow("Пароль:", password_input)

        remember_checkbox = QCheckBox("Запомнить учетные данные")
        remember_checkbox.setChecked(self.settings.get('remember_credentials', False))
        layout.addRow(remember_checkbox)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        if dialog.exec() == QDialog.Accepted:
            url = url_input.text().strip()
            username = username_input.text().strip()
            password = password_input.text()
            remember = remember_checkbox.isChecked()

            if not url or not username or not password:
                QMessageBox.warning(self, "Внимание", "Заполните все поля подключения")
                return

            # Сохраняем настройки
            self.settings.set_api_url(url)
            self.settings.set_credentials(username, password, remember)

            # Обновляем клиент
            self.api_client = APIClient(url)
            self.api_client.set_credentials(username, password)

            # Проверяем подключение
            self.connect_to_server(show_dialog=False)

    def connect_to_server(self, show_dialog=True):
        """Подключается к серверу"""
        self.status_bar.showMessage("Подключение к серверу...")
        self.current_worker = WorkerThread(self.api_client.test_connection)
        self.current_worker.finished.connect(self.on_connection_test)
        self.current_worker.error.connect(self.on_connection_error)
        self.current_worker.start()

    def disconnect_from_server(self):
        """Отключается от сервера"""
        self.api_client.clear_credentials()
        self.update_connection_status(False)
        self.status_bar.showMessage("Отключено", 5000)

    def toggle_remember_credentials(self, checked):
        """Переключает запоминание учетных данных"""
        self.settings.set('remember_credentials', checked)
        if not checked:
            self.settings.clear_credentials()

    def update_connection_status(self, connected):
        """Обновляет статус подключения"""
        if connected:
            self.status_bar.showMessage("● Подключено", 0)
            self.status_bar.setStyleSheet("QStatusBar { color: green; }")
        else:
            self.status_bar.showMessage("○ Не подключено", 0)
            self.status_bar.setStyleSheet("QStatusBar { color: red; }")

    def on_connection_test(self, result):
        """Обрабатывает результат проверки подключения"""
        if result:
            self.update_connection_status(True)
            self.load_user_info()
        else:
            self.update_connection_status(False)

    def on_connection_error(self, error_msg):
        """Обрабатывает ошибку подключения"""
        self.update_connection_status(False)
        QMessageBox.critical(self, "Ошибка подключения", error_msg)

    def clear_credentials(self):
        """Очищает сохраненные учетные данные"""
        self.settings.clear_credentials()
        self.disconnect_from_server()
        QMessageBox.information(self, "Успешно", "Сохраненные пароли очищены")

    def show_about(self):
        """Показывает информацию о программе"""
        QMessageBox.about(self, "О программе",
                         "TLog Search\n\n"
                         "Компактный клиент для поиска QSO в логбуке TLog\n\n"
                         "Версия: 1.0.0\n\n"
                         "Горячие клавиши:\n"
                         "Ctrl+K - Подключиться\n"
                         "Ctrl+D - Отключиться\n"
                         "Ctrl+Q - Выход")

    # ===== Обработка смены вкладки =====

    def on_tab_changed(self, index):
        """Обрабатывает смену вкладки"""
        if index == 0:  # Поиск
            pass
        elif index == 1:  # Статистика
            pass
        elif index == 2:  # Профиль
            pass

    # ===== Поиск =====

    def perform_search(self):
        """Выполняет поиск через API"""
        search_type = self.search_tab.search_type_combo.currentIndex()
        search_query = self.search_tab.search_input.text().strip()

        if not search_query:
            QMessageBox.warning(self, "Внимание", "Введите строку для поиска")
            return

        # Сохраняем тип поиска
        search_type_map = {0: 'callsign', 1: 'grid'}
        self.settings.set('last_search_type', search_type_map[search_type])

        self.status_bar.showMessage("Поиск...")

        if search_type == 0:  # По позывному
            self.current_worker = WorkerThread(self.api_client.search_by_callsign, search_query)
        else:  # По QTH локатору
            self.current_worker = WorkerThread(self.api_client.search_by_grid, search_query)

        self.current_worker.finished.connect(self.on_search_results)
        self.current_worker.error.connect(self.on_api_error)
        self.current_worker.start()

    def on_search_results(self, results):
        """Обрабатывает результаты поиска"""
        populate_compact_table(self.search_tab.search_table, results)
        self.status_bar.showMessage(f"Найдено {len(results)} записей (сервер)", 5000)

    def clear_search(self):
        """Очищает результаты поиска"""
        self.search_tab.search_table.setRowCount(0)
        self.search_tab.search_input.clear()

    # ===== Статистика =====

    def load_stats(self):
        """Загружает статистику"""
        self.status_bar.showMessage("Загрузка статистики...")
        self.current_worker = WorkerThread(self.api_client.get_stats)
        self.current_worker.finished.connect(self.on_stats_loaded)
        self.current_worker.error.connect(self.on_api_error)
        self.current_worker.start()

    def on_stats_loaded(self, stats):
        """Обрабатывает загруженную статистику"""
        text = "=== СТАТИСТИКА QSO ===\n\n"
        text += f"Всего QSO: {stats.get('total_qso', 0)}\n"
        text += f"Уникальных позывных: {stats.get('unique_callsigns', 0)}\n"
        text += f"Стран DXCC: {stats.get('dxcc_count', 0)}\n\n"

        text += "=== ПО ДИАПАЗОНАМ ===\n"
        for band, count in stats.get('band_statistics', {}).items():
            text += f"{band}: {count}\n"

        text += "\n=== ПО РЕЖИМАМ ===\n"
        for mode, count in stats.get('mode_statistics', {}).items():
            text += f"{mode}: {count}\n"

        text += "\n=== ПО ГОДАМ ===\n"
        for year, count in sorted(stats.get('year_statistics', {}).items(), reverse=True):
            text += f"{year}: {count}\n"

        self.stats_tab.stats_text.setText(text)
        self.status_bar.showMessage("Статистика загружена", 5000)

    # ===== Профиль =====

    def load_profile(self):
        """Загружает профиль пользователя"""
        self.status_bar.showMessage("Загрузка профиля...")
        self.current_worker = WorkerThread(self.api_client.get_profile)
        self.current_worker.finished.connect(self.on_profile_loaded)
        self.current_worker.error.connect(self.on_api_error)
        self.current_worker.start()

    def on_profile_loaded(self, profile):
        """Обрабатывает загруженный профиль"""
        text = "=== ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ ===\n\n"
        for key, value in profile.items():
            text += f"{key}: {value}\n"

        self.profile_tab.profile_text.setText(text)
        self.status_bar.showMessage("Профиль загружен", 5000)

    def load_user_info(self):
        """Загружает информацию о пользователе"""
        try:
            info = self.api_client.get_user_info()
            self.update_connection_status(True)
        except Exception as e:
            self.update_connection_status(False)

    def on_api_error(self, error_msg):
        """Обрабатывает ошибку API"""
        self.status_bar.showMessage("Ошибка", 5000)
        QMessageBox.critical(self, "Ошибка API", error_msg)

    def closeEvent(self, event):
        """Обрабатывает закрытие окна"""
        import base64
        geometry = self.saveGeometry().data()
        self.settings.set('window_geometry', base64.b64encode(geometry).decode('utf-8'))

        # Сохраняем размер окна
        size = self.size()
        self.settings.set('window_width', size.width())
        self.settings.set('window_height', size.height())

        event.accept()
