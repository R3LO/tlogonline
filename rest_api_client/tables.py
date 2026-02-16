"""
Настройка таблиц QSO
"""
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor
from typing import List
from datetime import datetime


def setup_compact_table(table: QTableWidget):
    """Настраивает компактную таблицу QSO"""
    table.setColumnCount(8)
    table.setHorizontalHeaderLabels([
        "DATE", "CALL", "BAND", "MODE", "DXCC", "LOC", "LOTW", "RST"
    ])

    header = table.horizontalHeader()
    header.setStretchLastSection(True)
    # Колонки можно менять вручную
    for i in range(7):
        header.setSectionResizeMode(i, QHeaderView.Interactive)
    header.setSectionResizeMode(7, QHeaderView.Stretch)

    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setAlternatingRowColors(True)
    table.setSortingEnabled(False)
    table.verticalHeader().setVisible(False)
    table.setShowGrid(True)  # Включаем сетку
    table.setStyleSheet("""
        QTableWidget {
            border: 1px solid #ccc;
            alternate-background-color: #f5f5f5;
            background-color: white;
            gridline-color: #ddd;
        }
        QTableWidget::item {
            padding: 3px;
            border: 1px solid #ddd;
        }
        QTableWidget::item:selected {
            background-color: #0078d4;
            color: white;
        }
        QTableWidget::item:alternate:selected {
            background-color: #0078d4;
            color: white;
        }
        QHeaderView::section {
            background-color: #e0e0e0;
            padding: 4px;
            border: 1px solid #ccc;
            border-bottom: 2px solid #ccc;
            font-weight: bold;
        }
    """)


def setup_lotw_table(table: QTableWidget):
    """Настраивает таблицу LoTW QSO"""
    table.setColumnCount(9)
    table.setHorizontalHeaderLabels([
        "DATE", "CALL", "BAND", "MODE", "DXCC", "LOC",
        "LOTW DATE", "CQ", "ITU"
    ])

    header = table.horizontalHeader()
    header.setStretchLastSection(True)
    # Колонки можно менять вручную
    for i in range(8):
        header.setSectionResizeMode(i, QHeaderView.Interactive)
    header.setSectionResizeMode(8, QHeaderView.Stretch)

    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setAlternatingRowColors(True)
    table.setSortingEnabled(False)
    table.verticalHeader().setVisible(False)
    table.setShowGrid(True)  # Включаем сетку
    table.setStyleSheet("""
        QTableWidget {
            border: 1px solid #ccc;
            alternate-background-color: #f5f5f5;
            background-color: white;
            gridline-color: #ddd;
        }
        QTableWidget::item {
            padding: 3px;
            border: 1px solid #ddd;
        }
        QTableWidget::item:selected {
            background-color: #0078d4;
            color: white;
        }
        QTableWidget::item:alternate:selected {
            background-color: #0078d4;
            color: white;
        }
        QHeaderView::section {
            background-color: #e0e0e0;
            padding: 4px;
            border: 1px solid #ccc;
            border-bottom: 2px solid #ccc;
            font-weight: bold;
        }
    """)


def setup_full_table(table: QTableWidget):
    """Настраивает полную таблицу QSO"""
    table.setColumnCount(11)
    table.setHorizontalHeaderLabels([
        "DATE/TIME", "CALL", "BAND", "MODE",
        "RST S/R", "DXCC", "LOC", "LOTW", "CQ", "ITU", "NOTES"
    ])

    header = table.horizontalHeader()
    header.setStretchLastSection(True)
    # Колонки можно менять вручную
    for i in range(10):
        header.setSectionResizeMode(i, QHeaderView.Interactive)
    header.setSectionResizeMode(10, QHeaderView.Stretch)

    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setAlternatingRowColors(True)
    table.setSortingEnabled(False)
    table.verticalHeader().setVisible(False)
    table.setShowGrid(True)  # Включаем сетку
    table.setStyleSheet("""
        QTableWidget {
            border: 1px solid #ccc;
            alternate-background-color: #f5f5f5;
            background-color: white;
            gridline-color: #ddd;
        }
        QTableWidget::item {
            padding: 3px;
            border: 1px solid #ddd;
        }
        QTableWidget::item:selected {
            background-color: #0078d4;
            color: white;
        }
        QTableWidget::item:alternate:selected {
            background-color: #0078d4;
            color: white;
        }
        QHeaderView::section {
            background-color: #e0e0e0;
            padding: 4px;
            border: 1px solid #ccc;
            border-bottom: 2px solid #ccc;
            font-weight: bold;
        }
    """)


def populate_compact_table(table: QTableWidget, qsos: List[dict]):
    """Заполняет компактную таблицу QSO данными"""
    table.setRowCount(0)

    # Сортировка по дате (от новых к старым)
    qsos_sorted = sorted(qsos, key=lambda x: x.get('date', ''), reverse=True)

    for row, qso in enumerate(qsos_sorted):
        table.insertRow(row)

        # Сохраняем ID в первом элементе строки (скрытый)
        qso_id = qso.get('id')
        date_item = QTableWidgetItem()
        if qso_id:
            date_item.setData(Qt.UserRole, str(qso_id))

        # Дата/Время
        date_str = qso.get('date', '')
        time_str = qso.get('time', '')
        display_date = ''
        if date_str:
            try:
                if 'T' in date_str:
                    # Дата уже содержит время в ISO формате
                    dt = datetime.fromisoformat(date_str)
                    display_date = dt.strftime("%d.%m.%Y %H:%M")
                else:
                    # Дата без времени
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                    # Если есть отдельное поле time, используем его
                    if time_str:
                        try:
                            # Пробуем парсить время в формате HH:MM или HH:MM:SS
                            if ':' in time_str:
                                time_parts = time_str.split(':')
                                hour = int(time_parts[0])
                                minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                                dt = dt.replace(hour=hour, minute=minute)
                        except:
                            pass
                    display_date = dt.strftime("%d.%m.%Y %H:%M")
            except:
                display_date = date_str

        date_item.setText(display_date)
        table.setItem(row, 0, date_item)

        # Позывной
        table.setItem(row, 1, QTableWidgetItem(qso.get('callsign', '').upper()))

        # Диапазон
        table.setItem(row, 2, QTableWidgetItem(qso.get('band', '').upper()))

        # Режим
        table.setItem(row, 3, QTableWidgetItem(qso.get('mode', '').upper()))

        # DXCC
        table.setItem(row, 4, QTableWidgetItem(qso.get('dxcc', '')))

        # QTH локатор
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
        # Формируем RST без разделителя, если одно из значений пустое
        if rst_sent and rst_rcvd:
            rst_display = f"{rst_sent}/{rst_rcvd}"
        elif rst_sent:
            rst_display = rst_sent
        elif rst_rcvd:
            rst_display = rst_rcvd
        else:
            rst_display = ''
        table.setItem(row, 7, QTableWidgetItem(rst_display))


def populate_lotw_table(table: QTableWidget, qsos: List[dict]):
    """Заполняет таблицу LoTW QSO данными"""
    table.setRowCount(0)

    for row, qso in enumerate(qsos):
        table.insertRow(row)

        # Сохраняем ID в первом элементе строки (скрытый)
        qso_id = qso.get('id')
        date_item = QTableWidgetItem()
        if qso_id:
            date_item.setData(Qt.UserRole, str(qso_id))

        # Дата QSO (полная с годом)
        date_str = qso.get('date', '')
        time_str = qso.get('time', '')
        display_date = ''
        if date_str:
            try:
                if 'T' in date_str:
                    dt = datetime.fromisoformat(date_str)
                else:
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                display_date = dt.strftime("%d.%m.%Y %H:%M")
            except:
                display_date = date_str

        date_item.setText(display_date)
        table.setItem(row, 0, date_item)

        # Позывной
        table.setItem(row, 1, QTableWidgetItem(qso.get('callsign', '').upper()))

        # Диапазон
        table.setItem(row, 2, QTableWidgetItem(qso.get('band', '').upper()))

        # Режим
        table.setItem(row, 3, QTableWidgetItem(qso.get('mode', '').upper()))

        # DXCC
        table.setItem(row, 4, QTableWidgetItem(qso.get('dxcc', '')))

        # QTH локатор
        table.setItem(row, 5, QTableWidgetItem(qso.get('gridsquare', '')))

        # LoTW дата получения подтверждения
        lotw_date = qso.get('app_lotw_rxqsl', '')
        if lotw_date:
            try:
                dt = datetime.fromisoformat(lotw_date)
                lotw_date = dt.strftime("%d.%m.%Y %H:%M")
            except:
                pass
        lotw_date_item = QTableWidgetItem(lotw_date)
        lotw_date_item.setForeground(QBrush(QColor(0, 150, 0)))  # Зелёный цвет
        table.setItem(row, 6, lotw_date_item)

        # CQ зона
        cqz = qso.get('cqz')
        table.setItem(row, 7, QTableWidgetItem(str(cqz) if cqz else ""))

        # ITU зона
        ituz = qso.get('ituz')
        table.setItem(row, 8, QTableWidgetItem(str(ituz) if ituz else ""))


def populate_full_table(table: QTableWidget, qsos: List[dict]):
    """Заполняет полную таблицу QSO данными"""
    table.setRowCount(0)

    # Сортировка по дате (от новых к старым)
    qsos_sorted = sorted(qsos, key=lambda x: x.get('date', ''), reverse=True)

    for row, qso in enumerate(qsos_sorted):
        table.insertRow(row)

        # Сохраняем ID в первом элементе строки (скрытый)
        qso_id = qso.get('id')
        date_item = QTableWidgetItem()
        if qso_id:
            date_item.setData(Qt.UserRole, str(qso_id))

        # Дата/Время
        date_str = qso.get('date', '')
        time_str = qso.get('time', '')
        display_date = ''
        if date_str:
            try:
                if 'T' in date_str:
                    dt = datetime.fromisoformat(date_str)
                else:
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                display_date = dt.strftime("%d.%m.%Y %H:%M")
            except:
                display_date = date_str

        date_item.setText(display_date)
        table.setItem(row, 0, date_item)

        # Позывной
        table.setItem(row, 1, QTableWidgetItem(qso.get('callsign', '').upper()))

        # Диапазон
        table.setItem(row, 2, QTableWidgetItem(qso.get('band', '').upper()))

        # Режим
        table.setItem(row, 3, QTableWidgetItem(qso.get('mode', '').upper()))

        # RST S/R
        rst_sent = qso.get('rst_sent', '')
        rst_rcvd = qso.get('rst_rcvd', '')
        # Формируем RST без разделителя, если одно из значений пустое
        if rst_sent and rst_rcvd:
            rst_display = f"{rst_sent}/{rst_rcvd}"
        elif rst_sent:
            rst_display = rst_sent
        elif rst_rcvd:
            rst_display = rst_rcvd
        else:
            rst_display = ''
        table.setItem(row, 4, QTableWidgetItem(rst_display))

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


def get_selected_qso_id(table: QTableWidget) -> str:
    """Получает ID выбранного QSO из таблицы"""
    row = table.currentRow()
    if row < 0:
        return None

    qso_id_item = table.item(row, 0)
    if not qso_id_item:
        return None

    return qso_id_item.data(Qt.UserRole)
