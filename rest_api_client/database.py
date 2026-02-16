"""
Локальная база данных SQLite для хранения QSO
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class LocalDatabase:
    """Локальная база данных SQLite"""

    def __init__(self):
        # Определяем путь к базе данных
        self.config_dir = Path.home() / '.tlog_rest_client'
        self.db_path = self.config_dir / 'qsos.db'

        # Создаем директорию, если она не существует
        self.config_dir.mkdir(exist_ok=True)

        # Создаем базу данных
        self._create_tables()

    def _get_connection(self):
        """Получает соединение с базой данных"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self):
        """Создает таблицы в базе данных"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Таблица QSO
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qsos (
                id TEXT PRIMARY KEY,
                callsign TEXT NOT NULL,
                date TEXT,
                time TEXT,
                my_callsign TEXT,
                frequency REAL,
                band TEXT,
                mode TEXT,
                rst_sent TEXT,
                rst_rcvd TEXT,
                my_gridsquare TEXT,
                gridsquare TEXT,
                continent TEXT,
                state TEXT,
                prop_mode TEXT,
                sat_name TEXT,
                r150s TEXT,
                dxcc TEXT,
                cqz INTEGER,
                ituz INTEGER,
                app_lotw_rxqsl TEXT,
                vucc_grids TEXT,
                iota TEXT,
                lotw TEXT,
                paper_qsl TEXT,
                created_at TEXT,
                updated_at TEXT,
                local_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Миграция: добавляем недостающие столбцы в существующую таблицу
        self._migrate_database(cursor)

        # Таблица для отслеживания синхронизации
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_info (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        # Индексы для быстрого поиска
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_qsos_callsign ON qsos(callsign)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_qsos_date ON qsos(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_qsos_lotw ON qsos(lotw)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_qsos_band ON qsos(band)')

        conn.commit()
        conn.close()

    def _migrate_database(self, cursor):
        """Выполняет миграцию базы данных, добавляя недостающие столбцы"""
        # Получаем текущую схему таблицы qsos
        cursor.execute("PRAGMA table_info(qsos)")
        columns = {row[1] for row in cursor.fetchall()}

        # Список столбцов, которые должны быть
        required_columns = [
            'time', 'my_callsign', 'frequency', 'band', 'mode',
            'rst_sent', 'rst_rcvd', 'my_gridsquare', 'gridsquare',
            'continent', 'state', 'prop_mode', 'sat_name', 'r150s',
            'dxcc', 'cqz', 'ituz', 'app_lotw_rxqsl', 'vucc_grids',
            'iota', 'lotw', 'paper_qsl', 'created_at', 'updated_at',
            'local_updated_at'
        ]

        # Добавляем недостающие столбцы
        for column in required_columns:
            if column not in columns:
                try:
                    if column in ['cqz', 'ituz']:
                        cursor.execute(f'ALTER TABLE qsos ADD COLUMN {column} INTEGER')
                    elif column == 'frequency':
                        cursor.execute(f'ALTER TABLE qsos ADD COLUMN {column} REAL')
                    else:
                        # SQLite не поддерживает DEFAULT в ALTER TABLE, добавляем столбец без дефолтного значения
                        cursor.execute(f'ALTER TABLE qsos ADD COLUMN {column} TEXT')
                except sqlite3.OperationalError:
                    # Столбец уже существует или другая ошибка - игнорируем
                    pass

    def save_qsos(self, qsos: List[Dict]) -> int:
        """Сохраняет QSO в базу данных, обновляет существующие"""
        conn = self._get_connection()
        cursor = conn.cursor()

        saved_count = 0
        updated_count = 0

        for qso in qsos:
            qso_id = qso.get('id')
            if not qso_id:
                continue

            # Проверяем, существует ли QSO
            cursor.execute('SELECT id, updated_at FROM qsos WHERE id = ?', (qso_id,))
            existing = cursor.fetchone()

            qso_data = (
                qso_id,
                qso.get('callsign', ''),
                qso.get('date', ''),  # DateField
                str(qso.get('time', '')) if qso.get('time') else '',  # TimeField
                qso.get('my_callsign', ''),
                qso.get('frequency'),
                qso.get('band', ''),
                qso.get('mode', ''),
                qso.get('rst_sent', ''),
                qso.get('rst_rcvd', ''),
                qso.get('my_gridsquare', ''),
                qso.get('gridsquare', ''),
                qso.get('continent', ''),
                qso.get('state', ''),
                qso.get('prop_mode', ''),
                qso.get('sat_name', ''),
                qso.get('r150s', ''),
                qso.get('dxcc', ''),
                qso.get('cqz'),
                qso.get('ituz'),
                qso.get('app_lotw_rxqsl', ''),
                qso.get('vucc_grids', ''),
                qso.get('iota', ''),
                qso.get('lotw', 'N'),
                qso.get('paper_qsl', 'N'),
                str(qso.get('created_at', '')),
                str(qso.get('updated_at', '')),
            )

            if existing:
                # Проверяем, нужно ли обновлять (сравниваем updated_at)
                existing_updated = existing[1] or ''
                new_updated = str(qso.get('updated_at', ''))

                if new_updated and existing_updated != new_updated:
                    # Обновляем существующий
                    cursor.execute('''
                        UPDATE qsos SET
                            callsign = ?, date = ?, time = ?, my_callsign = ?,
                            frequency = ?, band = ?, mode = ?, rst_sent = ?, rst_rcvd = ?,
                            my_gridsquare = ?, gridsquare = ?, continent = ?, state = ?,
                            prop_mode = ?, sat_name = ?, r150s = ?, dxcc = ?,
                            cqz = ?, ituz = ?, app_lotw_rxqsl = ?, vucc_grids = ?,
                            iota = ?, lotw = ?, paper_qsl = ?, created_at = ?, updated_at = ?,
                            local_updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', qso_data[1:] + (qso_id,))
                    updated_count += 1
            else:
                # Вставляем новый
                cursor.execute('''
                    INSERT INTO qsos (
                        id, callsign, date, time, my_callsign, frequency, band, mode,
                        rst_sent, rst_rcvd, my_gridsquare, gridsquare, continent, state,
                        prop_mode, sat_name, r150s, dxcc, cqz, ituz, app_lotw_rxqsl,
                        vucc_grids, iota, lotw, paper_qsl, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', qso_data)
                saved_count += 1

        conn.commit()
        conn.close()
        return saved_count

    def get_qsos(self, limit: Optional[int] = None) -> List[Dict]:
        """Получает все QSO из базы данных"""
        conn = self._get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM qsos ORDER BY date DESC, time DESC'
        if limit:
            query += f' LIMIT {limit}'

        cursor.execute(query)
        rows = cursor.fetchall()

        qsos = []
        for row in rows:
            qso = dict(row)
            # Удаляем служебные поля
            qso.pop('local_updated_at', None)
            qsos.append(qso)

        conn.close()
        return qsos

    def get_qso_by_id(self, qso_id: str) -> Optional[Dict]:
        """Получает QSO по ID"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM qsos WHERE id = ?', (qso_id,))
        row = cursor.fetchone()

        conn.close()

        if row:
            qso = dict(row)
            qso.pop('local_updated_at', None)
            return qso
        return None

    def search_by_callsign(self, callsign: str) -> List[Dict]:
        """Ищет QSO по позывному"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT * FROM qsos WHERE callsign LIKE ? ORDER BY date DESC, time DESC',
            (f'%{callsign.upper()}%',)
        )
        rows = cursor.fetchall()

        qsos = []
        for row in rows:
            qso = dict(row)
            qso.pop('local_updated_at', None)
            qsos.append(qso)

        conn.close()
        return qsos

    def search_by_grid(self, grid: str) -> List[Dict]:
        """Ищет QSO по QTH локатору"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT * FROM qsos WHERE gridsquare LIKE ? ORDER BY date DESC, time DESC',
            (f'%{grid.upper()}%',)
        )
        rows = cursor.fetchall()

        qsos = []
        for row in rows:
            qso = dict(row)
            qso.pop('local_updated_at', None)
            qsos.append(qso)

        conn.close()
        return qsos

    def search_by_band(self, band: str) -> List[Dict]:
        """Ищет QSO по диапазону"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT * FROM qsos WHERE band LIKE ? ORDER BY date DESC, time DESC',
            (f'%{band.upper()}%',)
        )
        rows = cursor.fetchall()

        qsos = []
        for row in rows:
            qso = dict(row)
            qso.pop('local_updated_at', None)
            qsos.append(qso)

        conn.close()
        return qsos

    def get_lotw_qsos(self) -> List[Dict]:
        """Получает QSO подтверждённые через LoTW"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM qsos
            WHERE lotw = 'Y'
            ORDER BY app_lotw_rxqsl DESC
        ''')
        rows = cursor.fetchall()

        qsos = []
        for row in rows:
            qso = dict(row)
            qso.pop('local_updated_at', None)
            qsos.append(qso)

        conn.close()
        return qsos

    def get_last_sync_date(self) -> Optional[str]:
        """Получает дату последней синхронизации"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM sync_info WHERE key = 'last_sync_date'")
        row = cursor.fetchone()

        conn.close()

        return row[0] if row else None

    def set_last_sync_date(self, date: str):
        """Устанавливает дату последней синхронизации"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO sync_info (key, value)
            VALUES ('last_sync_date', ?)
        ''', (date,))

        conn.commit()
        conn.close()

    def get_qso_count(self) -> int:
        """Возвращает общее количество QSO"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM qsos')
        count = cursor.fetchone()[0]

        conn.close()
        return count

    def delete_qso(self, qso_id: str) -> bool:
        """Удаляет QSO из базы данных"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM qsos WHERE id = ?', (qso_id,))
        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()
        return deleted

    def clear_all(self):
        """Очищает все QSO из базы данных"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM qsos')
        cursor.execute('DELETE FROM sync_info')

        conn.commit()
        conn.close()

    def drop_and_recreate(self):
        """Пересоздаёт базу данных (для миграции схемы)"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('DROP TABLE IF EXISTS qsos')
        cursor.execute('DROP TABLE IF EXISTS sync_info')

        conn.commit()
        conn.close()

        # Пересоздаём таблицы
        self._create_tables()
