#!/usr/bin/env python3
"""
Тест для проверки работы фильтров LoTW
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from tlog.models import QSO, RadioProfile
from datetime import date, time

def test_lotw_data():
    """Проверяем наличие данных LoTW в базе"""
    print("=== Проверка данных LoTW ===")
    
    # Проверяем пользователей
    users = User.objects.all()
    print(f"Всего пользователей: {users.count()}")
    
    if users.count() == 0:
        print("Создаем тестового пользователя...")
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Создаем профиль
        profile = RadioProfile.objects.create(
            user=user,
            callsign='TEST'
        )
        print(f"Создан пользователь: {user.username}")
    else:
        user = users.first()
        print(f"Используем пользователя: {user.username}")
    
    # Проверяем QSO
    all_qso = QSO.objects.filter(user=user)
    print(f"Всего QSO у пользователя: {all_qso.count()}")
    
    # Проверяем LoTW QSO
    lotw_qso = QSO.objects.filter(user=user, lotw='Y')
    print(f"LoTW QSO: {lotw_qso.count()}")
    
    # Проверяем LoTW с подтверждением
    lotw_confirmed = QSO.objects.filter(user=user, lotw='Y', app_lotw_rxqsl__isnull=False)
    print(f"LoTW подтвержденные: {lotw_confirmed.count()}")
    
    if lotw_confirmed.count() == 0:
        print("Создаем тестовые LoTW QSO...")
        # Создаем несколько тестовых QSO с LoTW подтверждением
        test_qso_data = [
            {
                'date': date(2024, 1, 15),
                'time': time(10, 30),
                'my_callsign': 'TEST',
                'callsign': 'W1AW',
                'band': '20m',
                'mode': 'CW',
                'lotw': 'Y',
                'app_lotw_rxqsl': date(2024, 1, 20),
                'gridsquare': 'FN31pr',
                'cqz': 5,
                'ituz': 8,
                'continent': 'NA',
                'r150s': 'United States',
                'dxcc': 'K'
            },
            {
                'date': date(2024, 2, 10),
                'time': time(14, 15),
                'my_callsign': 'TEST',
                'callsign': 'G0ABC',
                'band': '40m',
                'mode': 'SSB',
                'lotw': 'Y',
                'app_lotw_rxqsl': date(2024, 2, 15),
                'gridsquare': 'IO91wm',
                'cqz': 14,
                'ituz': 27,
                'continent': 'EU',
                'r150s': 'United Kingdom',
                'dxcc': 'G'
            },
            {
                'date': date(2024, 3, 5),
                'time': time(08, 45),
                'my_callsign': 'TEST',
                'callsign': 'JA1XYZ',
                'band': '15m',
                'mode': 'FT8',
                'lotw': 'Y',
                'app_lotw_rxqsl': date(2024, 3, 8),
                'gridsquare': 'PM95sq',
                'cqz': 45,
                'ituz': 45,
                'continent': 'AS',
                'r150s': 'Japan',
                'dxcc': 'JA'
            }
        ]
        
        for qso_data in test_qso_data:
            QSO.objects.create(user=user, **qso_data)
        
        print(f"Создано {len(test_qso_data)} тестовых LoTW QSO")
    
    # Проверяем уникальные значения для фильтров
    lotw_confirmed = QSO.objects.filter(user=user, lotw='Y', app_lotw_rxqsl__isnull=False)
    
    modes = lotw_confirmed.filter(mode__isnull=False, mode__gt='').values_list('mode', flat=True).distinct()
    bands = lotw_confirmed.filter(band__isnull=False, band__gt='').values_list('band', flat=True).distinct()
    sat_names = lotw_confirmed.filter(sat_name__isnull=False, sat_name__gt='').values_list('sat_name', flat=True).distinct()
    my_callsigns = lotw_confirmed.filter(my_callsign__isnull=False, my_callsign__gt='').values_list('my_callsign', flat=True).distinct()
    
    print(f"Доступные моды: {list(modes)}")
    print(f"Доступные диапазоны: {list(bands)}")
    print(f"Доступные спутники: {list(sat_names)}")
    print(f"Мои позывные: {list(my_callsigns)}")
    
    print("=== Тестирование фильтров ===")
    
    # Тест фильтрации по моде
    filtered_by_mode = lotw_confirmed.filter(mode='CW')
    print(f"Фильтр по CW: {filtered_by_mode.count()} записей")
    
    # Тест фильтрации по диапазону
    filtered_by_band = lotw_confirmed.filter(band='20m')
    print(f"Фильтр по 20m: {filtered_by_band.count()} записей")
    
    # Тест фильтрации по позывному
    filtered_by_callsign = lotw_confirmed.filter(callsign__icontains='W1')
    print(f"Фильтр по позывному W1: {filtered_by_callsign.count()} записей")
    
    print("=== Тест завершен успешно ===")

if __name__ == '__main__':
    test_lotw_data()