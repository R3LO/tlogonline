#!/usr/bin/env python
"""
Тест исправленной страницы профиля
"""
import os
import sys
import json

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
sys.path.append('.')

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from tlog.models import RadioProfile

def test_fixed_profile():
    """Тестируем исправленную страницу профиля"""
    
    print("=== ТЕСТ ИСПРАВЛЕННОЙ СТРАНИЦЫ ПРОФИЛЯ ===")
    
    # Получаем пользователя R3LO
    try:
        user = User.objects.get(username='R3LO')
        print(f"✓ Пользователь: {user.username}")
    except User.DoesNotExist:
        print("✗ Пользователь R3LO не найден")
        return
    
    # Создаем клиент
    client = Client()
    client.force_login(user)
    
    # Получаем страницу профиля
    print("\n1. Получение страницы профиля...")
    response = client.get('/dashboard/profile/')
    print(f"   Статус: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Страница загружена успешно")
        
        content = response.content.decode('utf-8')
        
        # Проверяем script тег
        if 'id="callsigns-data"' in content:
            print("✓ Script тег найден")
            
            # Ищем данные в script теге
            import re
            match = re.search(r'<script[^>]*id="callsigns-data"[^>]*>(.*?)</script>', content, re.DOTALL)
            if match:
                script_content = match.group(1).strip()
                print(f"✓ Данные в script теге: {script_content}")
                
                try:
                    callsigns = json.loads(script_content)
                    print(f"✓ Парсинг JSON: {callsigns}")
                    print(f"✓ Количество позывных: {len(callsigns)}")
                    
                    # Тестируем сохранение
                    print(f"\n2. Тест сохранения...")
                    new_callsigns = callsigns + [{'name': 'R3LO/FIXED'}]
                    
                    post_data = {
                        'first_name': 'Тест',
                        'last_name': 'Пользователь',
                        'qth': 'Москва',
                        'my_gridsquare': 'KO85UU',
                        'email': user.email,
                        'my_callsigns_json': json.dumps(new_callsigns),
                        'use_lotw': 'on',
                        'lotw_user': 'R3LO',
                        'lotw_password': 'test123',
                    }
                    
                    save_response = client.post('/dashboard/profile/', post_data)
                    print(f"   Статус сохранения: {save_response.status_code}")
                    
                    if save_response.status_code in [200, 302]:
                        print("✓ Данные отправлены успешно")
                        
                        # Проверяем базу
                        profile = RadioProfile.objects.get(user=user)
                        print(f"   Позывные в базе: {profile.my_callsigns}")
                        
                        if len(profile.my_callsigns) > len(callsigns):
                            print("✓ Сохранение работает!")
                        else:
                            print("✗ Сохранение не сработало")
                    else:
                        print(f"✗ Ошибка сохранения: {save_response.status_code}")
                        
                except json.JSONDecodeError as e:
                    print(f"✗ Ошибка парсинга JSON: {e}")
            else:
                print("✗ Данные в script теге не найдены")
        else:
            print("✗ Script тег не найден")
    else:
        print(f"✗ Ошибка загрузки страницы: {response.status_code}")

if __name__ == '__main__':
    test_fixed_profile()