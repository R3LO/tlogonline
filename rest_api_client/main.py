"""
TLog REST API Client - Клиентское приложение для работы с REST API логбука
"""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# Абсолютный импорт вместо относительного
from rest_api_client.main_window import MainWindow


def main():
    """Главная функция приложения"""
    # В PySide6 6.10+ масштабирование включено по умолчанию
    app = QApplication(sys.argv)
    app.setApplicationName("TLog REST API Client")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("TLog")

    # Устанавливаем шрифт по умолчанию
    font = QFont("Segoe UI", 9)
    app.setFont(font)

    # Создаем и показываем главное окно
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
