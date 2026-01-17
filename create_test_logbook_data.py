#!/usr/bin/env python3
"""
Создание тестовых данных для логбука
"""
import os
import sys
import django

# Настройка Django
sys.path.append('/')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from tlog.models import QSO, RadioProfile
from datetime import datetime
import random

def create_test_user():
    """Создание тестового пользователя"""
    username = 'test_ham'
    email = 'test@ham.ru'

    # Удаляем пользователя если существует
    User.objects.filter(username=username).delete()

    # Создаем пользователя
    user = User.objects.create_user(
        username=username,
        email=email,
        password='test123',
        first_name='Иван',
        last_name='Радиолюбитель'
    )

    # Создаем профиль радиолюбителя
    profile = RadioProfile.objects.create(
        user=user,
        callsign='UA1ABC',  # Мой позывной
        name='Иван Петров',
        location='Санкт-Петербург',
        license_class='3',
        antenna_type='Диполь',
        antenna_height='10м',
        radio_model='Icom IC-7300',
        power_output='100Вт'
    )

    return user, profile

def create_test_qso_data(user):
    """Создание тестовых QSO записей"""

    # Примеры тестовых QSO
    test_qso_data = [
        {
            'callsign': 'W1AW',
            'name': 'ARRL Headquarters',
            'location': 'Newington, CT',
            'frequency': 14.205,
            'mode': 'CW',
            'signal_report': '599',
            'rst_sent': '599',
            'rst_received': '599',
            'notes': 'Тестовая связь с штаб-квартирой ARRL',
            'datetime': datetime(2025, 1, 10, 14, 30)
        },
        {
            'callsign': 'G0ABC',
            'name': 'John Smith',
            'location': 'London',
            'frequency': 14.230,
            'mode': 'SSB',
            'signal_report': '59',
            'rst_sent': '59',
            'rst_received': '57',
            'notes': 'Отличная связь с Англией',
            'datetime': datetime(2025, 1, 11, 16, 45)
        },
        {
            'callsign': 'JA1XYZ',
            'name': 'Tanaka San',
            'location': 'Tokyo',
            'frequency': 21.205,
            'mode': 'FT8',
            'signal_report': '-10',
            'rst_sent': '599',
            'rst_received': '599',
            'notes': 'Первая связь с Японией на FT8',
            'datetime': datetime(2025, 1, 12, 8, 15)
        },
        {
            'callsign': 'EA7ABC',
            'name': 'Carlos',
            'location': 'Madrid',
            'frequency': 7.205,
            'mode': 'SSB',
            'signal_report': '59',
            'rst_sent': '59',
            'rst_received': '59',
            'notes': 'Связь с Испанией на 40м',
            'datetime': datetime(2025, 1, 13, 19, 20)
        },
        {
            'callsign': 'VK2XYZ',
            'name': 'Steve',
            'location': 'Sydney',
            'frequency': 28.505,
            'mode': 'SSB',
            'signal_report': '57',
            'rst_sent': '57',
            'rst_received': '55',
            'notes': 'Связь с Австралией на 10м',
            'datetime': datetime(2025, 1, 14, 12, 10)
        },
        {
            'callsign': 'DL1ABC',
            'name': 'Klaus',
            'location': 'Berlin',
            'frequency': 3.505,
            'mode': 'CW',
            'signal_report': '599',
            'rst_sent': '599',
            'rst_received': '589',
            'notes': 'CW связь с Германией на 80м',
            'datetime': datetime(2025, 1, 15, 7, 30)
        }
    ]

    # Создаем QSO записи
    for qso_data in test_qso_data:
        QSO.objects.create(
            user=user,
            date_time=qso_data['datetime'],
            callsign=qso_data['callsign'],
            name=qso_data['name'],
            location=qso_data['location'],
            frequency=qso_data['frequency'],
            mode=qso_data['mode'],
            signal_report=qso_data['signal_report'],
            rst_sent=qso_data['rst_sent'],
            rst_received=qso_data['rst_received'],
            notes=qso_data['notes']
        )

def main():
    print("Создание тестовых данных для логбука...")

    # Создаем пользователя
    user, profile = create_test_user()
    print(f"Создан пользователь: {user.username}")
    print(f"Позывной: {profile.callsign}")
    print(f"Местоположение: {profile.location}")

    # Создаем тестовые QSO
    create_test_qso_data(user)
    print("Создано 6 тестовых QSO записей")

    print("\nТестовые данные готовы!")
    print("Для входа используйте:")
    print("Логин: test_ham")
    print("Пароль: test123")

if __name__ == '__main__':
    main()