#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функциональности фильтров LoTW
"""

import os
import sys
import django
import requests

# Добавляем текущую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from tlog.models import QSO, RadioProfile
from django.utils import timezone
from datetime import datetime, timedelta
import random

def create_test_user():
    """Создаёт тестового пользователя"""
    username = 'testuser'
    try:
        user = User.objects.get(username=username)
        print(f"✅ Пользователь {username} уже существует")
        return user
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            email='test@example.com',
            password='testpass123'
        )
        print(f"✅ Создан тестовый пользователь: {username}")
        return user

def create_test_qso(user, my_callsign='UA6ABC', callsign='UA0AAA', band='20m', mode='SSB'):
    """Создаёт тестовые QSO записи"""
    
    # Создаём профиль если его нет
    try:
        profile = RadioProfile.objects.get(user=user)
    except RadioProfile.DoesNotExist:
        profile = RadioProfile.objects.create(user=user)
        print(f"✅ Создан профиль для {user.username}")
    
    # Создаём несколько тестовых QSO
    qso_data = [
        {
            'my_callsign': my_callsign,
            'callsign': 'UA0AAA',
            'band': '20m',
            'mode': 'SSB',
            'gridsquare': 'LO01',
            'lotw': 'Y',
            'app_lotw_rxqsl': timezone.now() - timedelta(days=1)
        },
        {
            'my_callsign': my_callsign,
            'callsign': 'EU1ZZ',
            'band': '40m',
            'mode': 'CW',
            'gridsquare': 'KO33',
            'lotw': 'Y',
            'app_lotw_rxqsl': timezone.now() - timedelta(days=2)
        },
        {
            'my_callsign': my_callsign,
            'callsign': 'US2YZ',
            'band': '20m',
            'mode': 'SSB',
            'gridsquare': 'LO02',
            'lotw': 'Y',
            'app_lotw_rxqsl': timezone.now() - timedelta(days=3)
        },
        {
            'my_callsign': 'UA6XYZ',
            'callsign': 'RA3AA',
            'band': '15m',
            'mode': 'RTTY',
            'gridsquare': 'LO11',
            'lotw': 'Y',
            'app_lotw_rxqsl': timezone.now() - timedelta(days=4)
        },
    ]
    
    created_count = 0
    for data in qso_data:
        qso, created = QSO.objects.get_or_create(
            user=user,
            callsign=data['callsign'],
            band=data['band'],
            mode=data['mode'],
            defaults=data
        )
        if created:
            created_count += 1
    
    print(f"✅ Создано {created_count} новых тестовых QSO")
    return created_count

def test_lotw_page():
    """Тестирует доступность страницы LoTW"""
    try:
        response = requests.get('http://127.0.0.1:8000/lotw/', timeout=5)
        print(f"📄 Статус страницы LoTW: {response.status_code}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка доступа к странице LoTW: {e}")
        return False

def main():
    print("🧪 Тестирование функциональности фильтров LoTW")
    print("=" * 50)
    
    # Создаём тестового пользователя
    user = create_test_user()
    
    # Создаём тестовые QSO
    qso_count = create_test_qso(user)
    
    # Тестируем доступность страницы
    if test_lotw_page():
        print("✅ Страница LoTW доступна")
    else:
        print("❌ Страница LoTW недоступна")
    
    print("\n📋 Инструкции для тестирования:")
    print("1. Откройте http://127.0.0.1:8000/lotw/")
    print("2. Войдите как testuser / testpass123")
    print("3. Примените любые фильтры")
    print("4. Проверьте появление уведомления 'Применены фильтры:' с бейджами")
    print("\n🎯 Ожидаемый результат:")
    print("- При применении фильтров появляется блок уведомлений")
    print("- В блоке показывается заголовок 'Применены фильтры:'")
    print("- Активные фильтры отображаются в виде цветных бейджей")
    print("- Бейджи содержат иконки и описания фильтров")

if __name__ == '__main__':
    main()