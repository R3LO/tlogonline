"""
Диалог создания/редактирования QSO
"""
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDateEdit, QCheckBox,
    QTextEdit, QDialogButtonBox, QSpinBox
)
from PySide6.QtCore import Qt, QDateTime
from typing import Optional
from datetime import datetime


class QSOCreateDialog(QDialog):
    """Диалог создания/редактирования QSO"""

    def __init__(self, parent=None, qso_data: Optional[dict] = None):
        super().__init__(parent)
        self.qso_data = qso_data
        self.setWindowTitle("Создать QSO" if qso_data is None else "Редактировать QSO")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс диалога"""
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
