"""
Главное окно приложения с GUI
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QDialog, QDialogButtonBox, QFormLayout,
    QTextEdit, QCheckBox, QGroupBox, QComboBox, QSplitter,
    QStatusBar, QProgressBar, QDateEdit, QSpinBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt, QThread, Signal, QDateTime, QSize
from PySide6.QtGui import QAction, QIcon, QColor, QBrush
from typing import Optional
from datetime import datetime

from rest_api_client.api_client import APIClient
from rest_api_client.settings import Settings


class WorkerThread(QThread):
    """Поток для выполнения API запросов в фоне"""
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class QSOCreateDialog(QDialog):
    """Диалог создания/редактирования QSO"""

    def __init__(self, parent=None, qso_data: Optional[dict] = None):
        super().__init__(parent)
        self.qso_data = qso_data
        self.setWindowTitle("Создать QSO" if qso_data is None else "Редактировать QSO")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)

        self.callsign_input = QLineEdit()
        layout.addRow("Позывной:", self.callsign_input)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDateTime.currentDateTime().date())
        layout.addRow("Дата:", self.date_input)

        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("HH:MM:SS")
        self.time_input.setText(QDateTime.currentDateTime().toString("HH:mm:ss"))
        layout.addRow("Время:", self.time_input)

        self.band_input = QLineEdit()
        self.band_input.setPlaceholderText("20M, 40M, 2M...")
        layout.addRow("Диапазон:", self.band_input)

        self.mode_input = QLineEdit()
        self.mode_input.setPlaceholderText("SSB, CW, FT8...")
        layout.addRow("Режим:", self.mode_input)

        self.rst_sent_input = QLineEdit()
        self.rst_sent_input.setText("59")
        layout.addRow("RST отправлено:", self.rst_sent_input)

        self.rst_rcvd_input = QLineEdit()
        self.rst_rcvd_input.setText("59")
        layout.addRow("RST получено:", self.rst_rcvd_input)

        self.gridsquare_input = QLineEdit()
        self.gridsquare_input.setPlaceholderText("KO85ab")
        layout.addRow("QTH локатор:", self.gridsquare_input)

        self.dxcc_input = QLineEdit()
        layout.addRow("DXCC:", self.dxcc_input)

        self.cqz_input = QSpinBox()
        self.cqz_input.setRange(1, 40)
        self.cqz_input.setSpecialValueText("-")
        layout.addRow("CQ зона:", self.cqz_input)

        self.ituz_input = QSpinBox()
        self.ituz_input.setRange(1, 90)
        self.ituz_input.setSpecialValueText("-")
        layout.addRow("ITU зона:", self.ituz_input)

        self.iota_input = QLineEdit()
        self.iota_input.setPlaceholderText("EU-001")
        layout.addRow("IOTA:", self.iota_input)

        self.lotw_input = QCheckBox()
        layout.addRow("LoTW:", self.lotw_input)

        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        layout.addRow("Заметки:", self.notes_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        # Заполняем данные при редактировании
        if self.qso_data:
            self.fill_data()

    def fill_data(self):
        """Заполняет поля данными QSO"""
        self.callsign_input.setText(self.qso_data.get('callsign', ''))
        if self.qso_data.get('date'):
            dt = datetime.fromisoformat(self.qso_data['date'])
            self.date_input.setDate(dt.date())
            self.time_input.setText(dt.strftime("%H:%M:%S"))
        self.band_input.setText(self.qso_data.get('band', ''))
        self.mode_input.setText(self.qso_data.get('mode', ''))
        self.rst_sent_input.setText(self.qso_data.get('rst_sent', ''))
        self.rst_rcvd_input.setText(self.qso_data.get('rst_rcvd', ''))
        self.gridsquare_input.setText(self.qso_data.get('gridsquare', ''))
        self.dxcc_input.setText(self.qso_data.get('dxcc', ''))
        if self.qso_data.get('cqz'):
            self.cqz_input.setValue(self.qso_data['cqz'])
        if self.qso_data.get('ituz'):
            self.ituz_input.setValue(self.qso_data['ituz'])
        self.iota_input.setText(self.qso_data.get('iota', ''))
        self.lotw_input.setChecked(self.qso_data.get('lotw') == 'Y')
        self.notes_input.setPlainText(self.qso_data.get('notes', ''))

    def get_data(self):
        """Возвращает данные QSO"""
        date_str = self.date_input.date().toString("yyyy-MM-dd")
        time_str = self.time_input.text() or "00:00:00"
        datetime_str = f"{date_str}T{time_str}"

        return {
            'callsign': self.callsign_input.text().upper(),
            'date': datetime_str,
            'band': self.band_input.text().upper(),
            'mode': self.mode_input.text().upper(),
            'rst_sent': self.rst_sent_input.text(),
            'rst_rcvd': self.rst_rcvd_input.text(),
            'gridsquare': self.gridsquare_input.text().upper(),
            'dxcc': self.dxcc_input.text(),
            'cqz': self.cqz_input.value() if self.cqz_input.value() > 0 else None,
            'ituz': self.ituz_input.value() if self.ituz_input.value() > 0 else None,
            'iota': self.iota_input.text().upper(),
            'lotw': 'Y' if self.lotw_input.isChecked() else 'N',
            'notes': self.notes_input.toPlainText(),
        }


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.api_client = APIClient(self.settings.get_api_url())
        self.current_worker = None

        self.setup_ui()
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
        main_layout.addWidget(self.tabs)

        # Создаем вкладки (поиск - первая и основная)
        self.create_search_tab()
        self.create_lotw_tab()
        self.create_qsos_tab()
        self.create_stats_tab()
        self.create_profile_tab()

        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_connection_status(False)

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

    def create_search_tab(self):
        """Создает вкладку поиска (основная)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        # Компактная панель поиска
        search_layout = QHBoxLayout()
        search_layout.setSpacing(6)

        self.search_type_combo = QComboBox()
        self.search_type_combo.addItems(["Позывной", "QTH локатор", "Диапазон"])
        self.search_type_combo.setMaximumWidth(120)
        search_layout.addWidget(QLabel("Тип:"))
        search_layout.addWidget(self.search_type_combo)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите строку для поиска...")
        self.search_input.returnPressed.connect(self.perform_search)
        search_layout.addWidget(self.search_input)

        self.search_btn = QPushButton("Найти")
        self.search_btn.setMaximumWidth(80)
        self.search_btn.setDefault(True)
        self.search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(self.search_btn)

        self.clear_search_btn = QPushButton("×")
        self.clear_search_btn.setMaximumWidth(40)
        self.clear_search_btn.setToolTip("Очистить")
        self.clear_search_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(self.clear_search_btn)

        layout.addLayout(search_layout)

        # Компактная таблица результатов
        self.search_table = QTableWidget()
        self.setup_compact_table(self.search_table)
        layout.addWidget(self.search_table)

        self.tabs.addTab(tab, "Поиск")
        self.tabs.setCurrentWidget(tab)  # Поиск - первая вкладка по умолчанию

    def create_lotw_tab(self):
        """Создает вкладку LoTW"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        # Панель поиска и управления
        control_layout = QHBoxLayout()
        control_layout.setSpacing(6)

        self.lotw_search_input = QLineEdit()
        self.lotw_search_input.setPlaceholderText("Поиск по позывному...")
        self.lotw_search_input.setMaximumWidth(200)
        self.lotw_search_input.returnPressed.connect(self.search_lotw_by_callsign)
        control_layout.addWidget(QLabel("Поиск:"))
        control_layout.addWidget(self.lotw_search_input)

        self.lotw_search_btn = QPushButton("Найти")
        self.lotw_search_btn.setMaximumWidth(80)
        self.lotw_search_btn.clicked.connect(self.search_lotw_by_callsign)
        control_layout.addWidget(self.lotw_search_btn)

        self.lotw_clear_search_btn = QPushButton("×")
        self.lotw_clear_search_btn.setMaximumWidth(40)
        self.lotw_clear_search_btn.setToolTip("Очистить")
        self.lotw_clear_search_btn.clicked.connect(self.clear_lotw_search)
        control_layout.addWidget(self.lotw_clear_search_btn)

        control_layout.addStretch()

        self.refresh_lotw_btn = QPushButton("Обновить")
        self.refresh_lotw_btn.setMaximumWidth(100)
        self.refresh_lotw_btn.clicked.connect(self.load_lotw_qsos)
        control_layout.addWidget(self.refresh_lotw_btn)

        # Информация о количестве
        self.lotw_count_label = QLabel("Загрузка...")
        control_layout.addWidget(self.lotw_count_label)

        layout.addLayout(control_layout)

        # Компактная таблица результатов LoTW
        self.lotw_table = QTableWidget()
        self.setup_lotw_table(self.lotw_table)
        layout.addWidget(self.lotw_table)

        self.tabs.addTab(tab, "LoTW")

    def create_qsos_tab(self):
        """Создает вкладку со списком QSO"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Панель управления
        control_layout = QHBoxLayout()

        self.refresh_qsos_btn = QPushButton("Обновить список")
        self.refresh_qsos_btn.clicked.connect(self.load_qsos)
        control_layout.addWidget(self.refresh_qsos_btn)

        self.create_qso_btn = QPushButton("Создать QSO")
        self.create_qso_btn.clicked.connect(self.create_qso)
        control_layout.addWidget(self.create_qso_btn)

        self.edit_qso_btn = QPushButton("Редактировать")
        self.edit_qso_btn.clicked.connect(self.edit_qso)
        control_layout.addWidget(self.edit_qso_btn)

        self.delete_qso_btn = QPushButton("Удалить")
        self.delete_qso_btn.clicked.connect(self.delete_qso)
        control_layout.addWidget(self.delete_qso_btn)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        # Таблица QSO
        self.qsos_table = QTableWidget()
        self.setup_qso_table(self.qsos_table)
        layout.addWidget(self.qsos_table)

        self.tabs.addTab(tab, "QSO")

    def create_stats_tab(self):
        """Создает вкладку статистики"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        control_layout = QHBoxLayout()
        self.refresh_stats_btn = QPushButton("Обновить статистику")
        self.refresh_stats_btn.clicked.connect(self.load_stats)
        control_layout.addWidget(self.refresh_stats_btn)
        control_layout.addStretch()
        layout.addLayout(control_layout)

        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        layout.addWidget(self.stats_text)

        self.tabs.addTab(tab, "Статистика")

    def create_profile_tab(self):
        """Создает вкладку профиля"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        control_layout = QHBoxLayout()
        self.refresh_profile_btn = QPushButton("Обновить профиль")
        self.refresh_profile_btn.clicked.connect(self.load_profile)
        control_layout.addWidget(self.refresh_profile_btn)
        control_layout.addStretch()
        layout.addLayout(control_layout)

        self.profile_text = QTextEdit()
        self.profile_text.setReadOnly(True)
        layout.addWidget(self.profile_text)

        self.tabs.addTab(tab, "Профиль")

    def setup_compact_table(self, table: QTableWidget):
        """Настраивает компактную таблицу QSO"""
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "Дата", "Позывной", "Диапазон", "Режим", "DXCC", "QTH", "LoTW", "RST"
        ])

        header = table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Дата
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Позывной
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Диапазон
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Режим
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # DXCC
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # QTH
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # LoTW
        header.setSectionResizeMode(7, QHeaderView.Stretch)           # RST

        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setAlternatingRowColors(True)
        table.setSortingEnabled(False)

    def setup_lotw_table(self, table: QTableWidget):
        """Настраивает таблицу LoTW QSO"""
        table.setColumnCount(9)
        table.setHorizontalHeaderLabels([
            "Дата QSO", "Позывной", "Диапазон", "Режим", "DXCC", "QTH",
            "LoTW дата", "CQ", "ITU"
        ])

        header = table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Дата QSO
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Позывной
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Диапазон
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Режим
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # DXCC
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # QTH
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # LoTW дата
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # CQ
        header.setSectionResizeMode(8, QHeaderView.Stretch)           # ITU

        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setAlternatingRowColors(False)
        table.setSortingEnabled(False)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setStyleSheet("""
            QTableWidget {
                border: none;
            }
            QTableWidget::item {
                padding: 2px;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setStyleSheet("""
            QTableWidget {
                border: none;
            }
            QTableWidget::item {
                padding: 2px;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
        table.setAlternatingRowColors(False)  # Без чередования для компактности

    def setup_qso_table(self, table: QTableWidget):
        """Настраивает полную таблицу QSO"""
        table.setColumnCount(11)
        table.setHorizontalHeaderLabels([
            "Дата/Время", "Позывной", "Диапазон", "Режим",
            "RST S/R", "DXCC", "QTH", "LoTW", "CQ", "ITU", "Заметки"
        ])

        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)

        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setAlternatingRowColors(True)
        table.setSortingEnabled(False)  # Сортировка будет программной

    def load_settings(self):
        """Загружает сохраненные настройки"""
        last_search_type = self.settings.get('last_search_type', 'callsign')
        self.search_type_combo.setCurrentIndex({
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
        # Проверяем подключение
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
            # Загружаем начальные данные
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

    # ===== Работа с QSO =====

    def load_qsos(self):
        """Загружает список всех QSO"""
        self.status_bar.showMessage("Загрузка QSO...")
        self.current_worker = WorkerThread(self.api_client.get_qsos)
        self.current_worker.finished.connect(self.on_qsos_loaded)
        self.current_worker.error.connect(self.on_api_error)
        self.current_worker.start()

    def on_qsos_loaded(self, qsos):
        """Обрабатывает загруженные QSO"""
        self.populate_qso_table(self.qsos_table, qsos)
        self.status_bar.showMessage(f"Загружено {len(qsos)} QSO", 5000)

    def populate_qso_table(self, table, qsos):
        """Заполняет таблицу QSO данными"""
        table.setRowCount(0)

        # Сортировка по дате (от новых к старым)
        qsos_sorted = sorted(qsos, key=lambda x: x.get('date', ''), reverse=True)

        # Определяем тип таблицы по количеству колонок
        is_compact = table.columnCount() == 8

        for row, qso in enumerate(qsos_sorted):
            table.insertRow(row)

            # Сохраняем ID в первом элементе строки (скрытый)
            qso_id = qso.get('id')
            date_item = QTableWidgetItem()
            if qso_id:
                date_item.setData(Qt.UserRole, str(qso_id))

            # Дата/Время
            date_time = qso.get('date', '')
            if date_time:
                try:
                    dt = datetime.fromisoformat(date_time)
                    date_time = dt.strftime("%d.%m %H:%M" if is_compact else "%d.%m.%Y %H:%M")
                except:
                    pass
            date_item.setText(date_time)
            table.setItem(row, 0, date_item)

            # Позывной
            table.setItem(row, 1, QTableWidgetItem(qso.get('callsign', '').upper()))

            if is_compact:
                # Компактная таблица (8 колонок)
                table.setItem(row, 2, QTableWidgetItem(qso.get('band', '').upper()))
                table.setItem(row, 3, QTableWidgetItem(qso.get('mode', '').upper()))
                table.setItem(row, 4, QTableWidgetItem(qso.get('dxcc', '')))
                table.setItem(row, 5, QTableWidgetItem(qso.get('gridsquare', '')))

                # LoTW
                lotw = qso.get('lotw', 'N')
                lotw_item = QTableWidgetItem("✓" if lotw == 'Y' else "")
                if lotw == 'Y':
                    lotw_item.setForeground(QBrush(QColor(0, 150, 0)))
                    lotw_item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, 6, lotw_item)

                # RST S/R
                rst_sent = qso.get('rst_sent', '')
                rst_rcvd = qso.get('rst_rcvd', '')
                table.setItem(row, 7, QTableWidgetItem(f"{rst_sent}/{rst_rcvd}"))
            else:
                # Полная таблица (11 колонок)
                table.setItem(row, 2, QTableWidgetItem(qso.get('band', '').upper()))
                table.setItem(row, 3, QTableWidgetItem(qso.get('mode', '').upper()))

                # RST S/R
                rst_sent = qso.get('rst_sent', '')
                rst_rcvd = qso.get('rst_rcvd', '')
                table.setItem(row, 4, QTableWidgetItem(f"{rst_sent}/{rst_rcvd}"))

                # DXCC
                table.setItem(row, 5, QTableWidgetItem(qso.get('dxcc', '')))

                # QTH локатор
                table.setItem(row, 6, QTableWidgetItem(qso.get('gridsquare', '')))

                # LoTW
                lotw = qso.get('lotw', 'N')
                lotw_item = QTableWidgetItem("✓" if lotw == 'Y' else "")
                if lotw == 'Y':
                    lotw_item.setForeground(QBrush(QColor(0, 150, 0)))
                table.setItem(row, 7, lotw_item)

                # CQ зона
                cqz = qso.get('cqz')
                table.setItem(row, 8, QTableWidgetItem(str(cqz) if cqz else ""))

                # ITU зона
                ituz = qso.get('ituz')
                table.setItem(row, 9, QTableWidgetItem(str(ituz) if ituz else ""))

                # Заметки
                notes = qso.get('notes', '')
                if len(notes) > 50:
                    notes = notes[:50] + "..."
                table.setItem(row, 10, QTableWidgetItem(notes))

        table.resizeColumnsToContents()

    def create_qso(self):
        """Создает новое QSO"""
        dialog = QSOCreateDialog(self)
        if dialog.exec() == QDialog.Accepted:
            qso_data = dialog.get_data()
            self.status_bar.showMessage("Создание QSO...")
            self.current_worker = WorkerThread(self.api_client.create_qso, qso_data)
            self.current_worker.finished.connect(lambda r: self.on_qso_created(r, dialog))
            self.current_worker.error.connect(self.on_api_error)
            self.current_worker.start()

    def on_qso_created(self, result, dialog):
        """Обрабатывает создание QSO"""
        self.status_bar.showMessage("QSO создано успешно", 5000)
        QMessageBox.information(self, "Успешно", "QSO успешно создано")
        self.load_qsos()

    # ===== LoTW =====

    def load_lotw_qsos(self):
        """Загружает список QSO подтверждённых через LoTW"""
        self.status_bar.showMessage("Загрузка LoTW QSO...")
        self.current_worker = WorkerThread(self.api_client.get_lotw_qsos)
        self.current_worker.finished.connect(self.on_lotw_qsos_loaded)
        self.current_worker.error.connect(self.on_api_error)
        self.current_worker.start()

    def on_lotw_qsos_loaded(self, qsos):
        """Обрабатывает загруженные LoTW QSO"""
        self.populate_lotw_table(qsos)
        self.lotw_count_label.setText(f"Всего: {len(qsos)}")
        self.status_bar.showMessage(f"Загружено {len(qsos)} LoTW QSO", 5000)

    def search_lotw_by_callsign(self):
        """Ищет QSO LoTW по позывному"""
        callsign = self.lotw_search_input.text().strip().upper()
        if not callsign:
            QMessageBox.warning(self, "Внимание", "Введите позывной для поиска")
            return

        self.status_bar.showMessage(f"Поиск LoTW QSO: {callsign}...")
        self.current_worker = WorkerThread(self.api_client.search_by_callsign, callsign)
        self.current_worker.finished.connect(self.on_lotw_search_results)
        self.current_worker.error.connect(self.on_api_error)
        self.current_worker.start()

    def on_lotw_search_results(self, results):
        """Обрабатывает результаты поиска LoTW"""
        # Фильтруем только LoTW подтверждённые
        lotw_results = [qso for qso in results if qso.get('lotw') == 'Y']
        self.populate_lotw_table(lotw_results)
        self.lotw_count_label.setText(f"Найдено: {len(lotw_results)}")
        self.status_bar.showMessage(f"Найдено {len(lotw_results)} LoTW QSO", 5000)

    def clear_lotw_search(self):
        """Очищает поиск на вкладке LoTW"""
        self.lotw_search_input.clear()
        self.load_lotw_qsos()

    def populate_lotw_table(self, qsos):
        """Заполняет таблицу LoTW QSO данными"""
        self.lotw_table.setRowCount(0)

        for row, qso in enumerate(qsos):
            self.lotw_table.insertRow(row)

            # Сохраняем ID в первом элементе строки (скрытый)
            qso_id = qso.get('id')
            date_item = QTableWidgetItem()
            if qso_id:
                date_item.setData(Qt.UserRole, str(qso_id))

            # Дата QSO (полная с годом)
            date_time = qso.get('date', '')
            if date_time:
                try:
                    dt = datetime.fromisoformat(date_time)
                    date_time = dt.strftime("%d.%m.%Y %H:%M")
                except:
                    pass
            date_item.setText(date_time)
            self.lotw_table.setItem(row, 0, date_item)

            # Позывной
            self.lotw_table.setItem(row, 1, QTableWidgetItem(qso.get('callsign', '').upper()))

            # Диапазон
            self.lotw_table.setItem(row, 2, QTableWidgetItem(qso.get('band', '').upper()))

            # Режим
            self.lotw_table.setItem(row, 3, QTableWidgetItem(qso.get('mode', '').upper()))

            # DXCC
            self.lotw_table.setItem(row, 4, QTableWidgetItem(qso.get('dxcc', '')))

            # QTH локатор
            self.lotw_table.setItem(row, 5, QTableWidgetItem(qso.get('gridsquare', '')))

            # LoTW дата получения подтверждения (полная с годом)
            lotw_date = qso.get('app_lotw_rxqsl', '')
            if lotw_date:
                try:
                    dt = datetime.fromisoformat(lotw_date)
                    lotw_date = dt.strftime("%d.%m.%Y %H:%M")
                except:
                    pass
            lotw_date_item = QTableWidgetItem(lotw_date)
            lotw_date_item.setForeground(QBrush(QColor(0, 150, 0)))  # Зелёный цвет
            self.lotw_table.setItem(row, 6, lotw_date_item)

            # CQ зона
            cqz = qso.get('cqz')
            self.lotw_table.setItem(row, 7, QTableWidgetItem(str(cqz) if cqz else ""))

            # ITU зона
            ituz = qso.get('ituz')
            self.lotw_table.setItem(row, 8, QTableWidgetItem(str(ituz) if ituz else ""))

        self.lotw_table.resizeColumnsToContents()

    def edit_qso(self):
        """Редактирует выбранное QSO"""
        current_tab = self.tabs.currentIndex()
        if current_tab == 1:  # Вкладка LoTW
            table = self.lotw_table
        elif current_tab == 2:  # Вкладка QSO
            table = self.qsos_table
        elif current_tab == 0:  # Вкладка поиска
            table = self.search_table
        else:
            return

        row = table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите QSO для редактирования")
            return

        # Получаем ID из первого элемента строки
        qso_id_item = table.item(row, 0)
        if not qso_id_item:
            QMessageBox.warning(self, "Внимание", "Не удалось получить ID QSO")
            return

        qso_id = qso_id_item.data(Qt.UserRole)
        if not qso_id:
            QMessageBox.warning(self, "Внимание", "Не удалось получить ID QSO")
            return

        # Загружаем данные QSO
        self.status_bar.showMessage("Загрузка QSO...")
        self.current_worker = WorkerThread(self.api_client.get_qso, qso_id)
        self.current_worker.finished.connect(lambda r: self.on_qso_loaded_for_edit(r))
        self.current_worker.error.connect(self.on_api_error)
        self.current_worker.start()

    def on_qso_loaded_for_edit(self, qso_data):
        """Обрабатывает загруженные данные QSO для редактирования"""
        dialog = QSOCreateDialog(self, qso_data)
        if dialog.exec() == QDialog.Accepted:
            qso_id = qso_data.get('id')
            updated_data = dialog.get_data()
            self.status_bar.showMessage("Обновление QSO...")
            self.current_worker = WorkerThread(
                self.api_client.partial_update_qso, qso_id, updated_data
            )
            self.current_worker.finished.connect(lambda r: self.on_qso_updated(r))
            self.current_worker.error.connect(self.on_api_error)
            self.current_worker.start()

    def on_qso_updated(self, result):
        """Обрабатывает обновление QSO"""
        self.status_bar.showMessage("QSO обновлено успешно", 5000)
        QMessageBox.information(self, "Успешно", "QSO успешно обновлено")
        # Обновляем текущую таблицу
        current_tab = self.tabs.currentIndex()
        if current_tab == 0:  # Поиск
            self.perform_search()
        elif current_tab == 1:  # LoTW
            self.load_lotw_qsos()
        else:  # QSO
            self.load_qsos()

    def delete_qso(self):
        """Удаляет выбранное QSO"""
        current_tab = self.tabs.currentIndex()
        if current_tab == 1:  # Вкладка LoTW
            table = self.lotw_table
        elif current_tab == 2:  # Вкладка QSO
            table = self.qsos_table
        elif current_tab == 0:  # Вкладка поиска
            table = self.search_table
        else:
            return

        row = table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите QSO для удаления")
            return

        # Получаем ID из первого элемента строки
        qso_id_item = table.item(row, 0)
        if not qso_id_item:
            QMessageBox.warning(self, "Внимание", "Не удалось получить ID QSO")
            return

        qso_id = qso_id_item.data(Qt.UserRole)
        if not qso_id:
            QMessageBox.warning(self, "Внимание", "Не удалось получить ID QSO")
            return

        # Подтверждение удаления
        callsign_item = table.item(row, 1)
        callsign = callsign_item.text() if callsign_item else "?"

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить QSO с {callsign}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.status_bar.showMessage("Удаление QSO...")
            self.current_worker = WorkerThread(self.api_client.delete_qso, qso_id)
            self.current_worker.finished.connect(lambda r: self.on_qso_deleted(r))
            self.current_worker.error.connect(self.on_api_error)
            self.current_worker.start()

    def on_qso_deleted(self, result):
        """Обрабатывает удаление QSO"""
        self.status_bar.showMessage("QSO удалено успешно", 5000)
        QMessageBox.information(self, "Успешно", "QSO успешно удалено")
        # Обновляем текущую таблицу
        current_tab = self.tabs.currentIndex()
        if current_tab == 0:  # Поиск
            self.perform_search()
        elif current_tab == 1:  # LoTW
            self.load_lotw_qsos()
        else:  # QSO
            self.load_qsos()

    # ===== Поиск =====

    def perform_search(self):
        """Выполняет поиск"""
        search_type = self.search_type_combo.currentIndex()
        search_query = self.search_input.text().strip()

        if not search_query:
            QMessageBox.warning(self, "Внимание", "Введите строку для поиска")
            return

        # Сохраняем тип поиска
        search_type_map = {0: 'callsign', 1: 'grid', 2: 'band'}
        self.settings.set('last_search_type', search_type_map[search_type])

        self.status_bar.showMessage("Поиск...")
        if search_type == 0:  # По позывному
            self.current_worker = WorkerThread(self.api_client.search_by_callsign, search_query)
        elif search_type == 1:  # По QTH локатору
            self.current_worker = WorkerThread(self.api_client.search_by_grid, search_query)
        else:  # По диапазону
            self.current_worker = WorkerThread(self.api_client.search_by_band, search_query)

        self.current_worker.finished.connect(self.on_search_results)
        self.current_worker.error.connect(self.on_api_error)
        self.current_worker.start()

    def on_search_results(self, results):
        """Обрабатывает результаты поиска"""
        self.populate_qso_table(self.search_table, results)
        self.status_bar.showMessage(f"Найдено {len(results)} записей", 5000)

    def clear_search(self):
        """Очищает результаты поиска"""
        self.search_table.setRowCount(0)
        self.search_input.clear()

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

        self.stats_text.setText(text)
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

        self.profile_text.setText(text)
        self.status_bar.showMessage("Профиль загружен", 5000)

    def load_user_info(self):
        """Загружает информацию о пользователе"""
        try:
            info = self.api_client.get_user_info()
            self.update_connection_status(True)
            # Автоматически загружаем LoTW QSO
            self.load_lotw_qsos()
        except Exception as e:
            self.update_connection_status(False)

    def on_api_error(self, error_msg):
        """Обрабатывает ошибку API"""
        self.status_bar.showMessage("Ошибка", 5000)
        QMessageBox.critical(self, "Ошибка API", error_msg)

    def closeEvent(self, event):
        """Обрабатывает закрытие окна"""
        # Сохраняем геометрию окна
        import base64
        geometry = self.saveGeometry().data()
        self.settings.set('window_geometry', base64.b64encode(geometry).decode('utf-8'))

        # Сохраняем размер окна
        size = self.size()
        self.settings.set('window_width', size.width())
        self.settings.set('window_height', size.height())

        event.accept()
