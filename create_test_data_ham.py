#!/usr/bin/env python
"""
Создание тестовых данных для сайта радиолюбителей
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from frontend.models import RadioProfile, QSO, ADIFUpload
from decimal import Decimal
from datetime import datetime, timedelta
import random

def create_test_data():
    """Создание тестовых данных"""
    print("Создание тестовых данных для сайта радиолюбителей...")

    # Создаем тестового радиолюбителя
    username = 'test_ham_operator'
    email = 'ham@example.com'
    password = 'testpass123'
    callsign = 'RA9XYZ'
    qth_locator = 'LO91AA'

    try:
        # Проверяем, существует ли пользователь
        user = User.objects.get(username=username)
        print(f'Пользователь {username} уже существует')
    except User.DoesNotExist:
        # Создаем нового пользователя
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name='Иван',
            last_name='Радиолюбитель'
        )
        print(f'Пользователь {username} создан успешно!')

        # Создаем профиль радиолюбителя
        profile = RadioProfile.objects.create(
            user=user,
            callsign=callsign,
            qth_locator=qth_locator,
            city='Новосибирск',
            country='Россия',
            radio_license_class='1',
            is_verified=True
        )
        print(f'Профиль радиолюбителя {callsign} создан успешно!')

    # Создаем тестовые QSO записи
    if not QSO.objects.filter(user=user).exists():
        print("Создание тестовых QSO записей...")

        qso_data = [
            {
                'my_callsign': callsign,
                'my_qth_locator': qth_locator,
                'counterpart_callsign': 'UA1ABC',
                'counterpart_qth_locator': 'KO85UU',
                'frequency': Decimal('14.205'),
                'mode': 'SSB',
                'date_time': datetime.now() - timedelta(days=1),
                'signal_report': '59',
                'notes': 'Отличная связь с Москвой'
            },
            {
                'my_callsign': callsign,
                'my_qth_locator': qth_locator,
                'counterpart_callsign': 'EW2ABC',
                'counterpart_qth_locator': 'KO33AA',
                'frequency': Decimal('7.050'),
                'mode': 'CW',
                'date_time': datetime.now() - timedelta(days=2),
                'signal_report': '599',
                'notes': 'CW связь с Беларусью'
            },
            {
                'my_callsign': callsign,
                'my_qth_locator': qth_locator,
                'counterpart_callsign': 'UR4ABC',
                'counterpart_qth_locator': 'KN28CA',
                'frequency': Decimal('21.200'),
                'mode': 'FT8',
                'date_time': datetime.now() - timedelta(days=3),
                'signal_report': 'S5',
                'notes': 'FT8 связь с Украиной'
            },
            {
                'my_callsign': callsign,
                'my_qth_locator': qth_locator,
                'counterpart_callsign': 'LA9ABC',
                'counterpart_qth_locator': 'JO59AA',
                'frequency': Decimal('144.500'),
                'mode': 'FM',
                'date_time': datetime.now() - timedelta(days=4),
                'signal_report': '59',
                'notes': 'FM связь с Норвегией'
            },
            {
                'my_callsign': callsign,
                'my_qth_locator': qth_locator,
                'counterpart_callsign': 'JA1ABC',
                'counterpart_qth_locator': 'PM95AA',
                'frequency': Decimal('28.500'),
                'mode': 'SSB',
                'date_time': datetime.now() - timedelta(days=5),
                'signal_report': '57',
                'notes': 'Дальняя связь с Японией'
            }
        ]

        for qso_info in qso_data:
            QSO.objects.create(user=user, **qso_info)

        print(f"Создано {len(qso_data)} тестовых QSO записей")

    print(f'''
Тестовый радиолюбитель готов:
Логин: {username}
Пароль: {password}
Позывной: {callsign}
QTH: {qth_locator}

Доступные страницы:
- Главная: http://localhost:8000/
- Регистрация: http://localhost:8000/register/
- Вход: http://localhost:8000/login/
- Панель: http://localhost:8000/dashboard/
- API: http://localhost:8000/api/

Статистика:
- Всего пользователей: {User.objects.count()}
- Всего профилей радиолюбителей: {RadioProfile.objects.count()}
- Всего QSO: {QSO.objects.count()}
    ''')

if __name__ == '__main__':
    create_test_data()