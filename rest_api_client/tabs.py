"""
Создание и управление вкладками
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTableWidget, QTextEdit, QTabWidget
)
from PySide6.QtCore import Signal

from rest_api_client.tables import (
    setup_compact_table, setup_lotw_table, setup_full_table
)


class SearchTab(QWidget):
    """Вкладка поиска QSO"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс вкладки"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        # Панель поиска
        search_layout = QHBoxLayout()
        search_layout.setSpacing(6)

        self.search_type_combo = QComboBox()
        self.search_type_combo.addItems(["Позывной", "QTH локатор"])
        self.search_type_combo.setMaximumWidth(120)
        search_layout.addWidget(QLabel("Тип:"))
        search_layout.addWidget(self.search_type_combo)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите строку для поиска...")
        search_layout.addWidget(self.search_input)

        self.search_btn = QPushButton("Найти")
        self.search_btn.setMaximumWidth(80)
        self.search_btn.setDefault(True)
        search_layout.addWidget(self.search_btn)

        self.clear_search_btn = QPushButton("×")
        self.clear_search_btn.setMaximumWidth(40)
        self.clear_search_btn.setToolTip("Очистить")
        search_layout.addWidget(self.clear_search_btn)

        layout.addLayout(search_layout)

        # Таблица результатов
        self.search_table = QTableWidget()
        setup_compact_table(self.search_table)
        layout.addWidget(self.search_table)


class LoTWTab(QWidget):
    """Вкладка LoTW QSO"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс вкладки"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        # Панель поиска и управления
        control_layout = QHBoxLayout()
        control_layout.setSpacing(6)

        self.lotw_search_input = QLineEdit()
        self.lotw_search_input.setPlaceholderText("Поиск по позывному...")
        self.lotw_search_input.setMaximumWidth(200)
        control_layout.addWidget(QLabel("Поиск:"))
        control_layout.addWidget(self.lotw_search_input)

        self.lotw_search_btn = QPushButton("Найти")
        self.lotw_search_btn.setMaximumWidth(80)
        control_layout.addWidget(self.lotw_search_btn)

        self.lotw_clear_search_btn = QPushButton("×")
        self.lotw_clear_search_btn.setMaximumWidth(40)
        self.lotw_clear_search_btn.setToolTip("Очистить")
        control_layout.addWidget(self.lotw_clear_search_btn)

        control_layout.addStretch()

        # Информация о количестве
        self.lotw_count_label = QLabel("Загрузка...")
        control_layout.addWidget(self.lotw_count_label)

        layout.addLayout(control_layout)

        # Таблица результатов LoTW
        self.lotw_table = QTableWidget()
        setup_lotw_table(self.lotw_table)
        layout.addWidget(self.lotw_table)


class QSOTab(QWidget):
    """Вкладка со списком QSO"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс вкладки"""
        layout = QVBoxLayout(self)

        # Панель управления
        control_layout = QHBoxLayout()

        self.create_qso_btn = QPushButton("Создать QSO")
        control_layout.addWidget(self.create_qso_btn)

        self.edit_qso_btn = QPushButton("Редактировать")
        control_layout.addWidget(self.edit_qso_btn)

        self.delete_qso_btn = QPushButton("Удалить")
        control_layout.addWidget(self.delete_qso_btn)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        # Таблица QSO
        self.qsos_table = QTableWidget()
        setup_full_table(self.qsos_table)
        layout.addWidget(self.qsos_table)


class StatsTab(QWidget):
    """Вкладка статистики"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс вкладки"""
        layout = QVBoxLayout(self)

        control_layout = QHBoxLayout()
        self.refresh_stats_btn = QPushButton("Обновить статистику")
        control_layout.addWidget(self.refresh_stats_btn)
        control_layout.addStretch()
        layout.addLayout(control_layout)

        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        layout.addWidget(self.stats_text)


class ProfileTab(QWidget):
    """Вкладка профиля"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс вкладки"""
        layout = QVBoxLayout(self)

        control_layout = QHBoxLayout()
        self.refresh_profile_btn = QPushButton("Обновить профиль")
        control_layout.addWidget(self.refresh_profile_btn)
        control_layout.addStretch()
        layout.addLayout(control_layout)

        self.profile_text = QTextEdit()
        self.profile_text.setReadOnly(True)
        layout.addWidget(self.profile_text)
