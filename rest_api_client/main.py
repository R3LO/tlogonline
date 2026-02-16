"""
TLog Search - Клиентское приложение для работы с REST API логбука
"""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from rest_api_client.main_window import MainWindow


def main():
    """Главная функция приложения"""
    app = QApplication(sys.argv)
    app.setApplicationName("TLog Search")
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
