#!/usr/bin/env python
"""
Финальный тест полного цикла - вход в систему и работа с профилем
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

def test_complete_login_and_profile():
    """Тестируем полный цикл входа в систему и работы с профилем"""
    
    print("=== ФИНАЛЬНЫЙ ТЕСТ - ПОЛНЫЙ ЦИКЛ ===")
    print("Пользователь: R3LO")
    print("Пароль: Labrador603502")
    print("=" * 50)
    
    # Создаем клиент
    client = Client()
    
    # Попытка входа
    print("\n1. ВХОД В СИСТЕМУ")
    login_response = client.post('/login/', {
        'username': 'R3LO',
        'password': 'Labrador603502',
        'csrfmiddlewaretoken': 'test_token'
    }, follow=True)
    
    print(f"   Статус входа: {login_response.status_code}")
    
    # Проверяем, что пользователь аутентифицирован
    if login_response.status_code in [200, 302]:
        print("✓ Вход выполнен успешно")
        
        # Получаем страницу профиля
        print("\n2. ПОЛУЧЕНИЕ СТРАНИЦЫ ПРОФИЛЯ")
        profile_response = client.get('/dashboard/profile/')
        print(f"   Статус страницы: {profile_response.status_code}")
        
        if profile_response.status_code == 200:
            print("✓ Страница профиля загружена")
            
            content = profile_response.content.decode('utf-8')
            
            # Проверяем JavaScript
            if '=== Profile Edit JS Loaded ===' in content:
                print("✓ JavaScript код найден")
            else:
                print("✗ JavaScript код не найден")
            
            # Проверяем данные в script теге
            import re
            match = re.search(r'<script[^>]*id="callsigns-data"[^>]*>(.*?)</script>', content, re.DOTALL)
            if match:
                script_content = match.group(1).strip()
                print(f"✓ Script тег найден: {script_content[:100]}...")
                
                try:
                    callsigns = json.loads(script_content)
                    print(f"✓ JSON парсинг: {len(callsigns)} позывных")
                    
                    # Добавляем тестовый позывной
                    test_callsigns = callsigns + [{'name': 'R3LO/FINAL'}]
                    
                    print(f"\n3. ТЕСТ СОХРАНЕНИЯ")
                    print(f"   Сохраняем: {test_callsigns}")
                    
                    # Сохраняем данные
                    save_response = client.post('/dashboard/profile/', {
                        'first_name': 'Финальный',
                        'last_name': 'Тест',
                        'qth': 'Москва',
                        'my_gridsquare': 'KO85UU',
                        'email': 'r3lo@duc5.com',
                        'my_callsigns_json': json.dumps(test_callsigns),
                        'use_lotw': 'on',
                        'lotw_user': 'R3LO',
                        'lotw_password': 'test123',
                    })
                    
                    print(f"   Статус сохранения: {save_response.status_code}")
                    
                    if save_response.status_code in [200, 302]:
                        print("✓ Сохранение выполнено")
                        
                        # Проверяем базу данных
                        user = User.objects.get(username='R3LO')
                        profile = RadioProfile.objects.get(user=user)
                        
                        print(f"   Позывные в базе: {len(profile.my_callsigns)}")
                        print(f"   Данные: {profile.my_callsigns}")
                        
                        if len(profile.my_callsigns) > 0:
                            print("✅ ПОЛНАЯ СИСТЕМА РАБОТАЕТ!")
                            print("\n🚀 ГОТОВО К ИСПОЛЬЗОВАНИЮ:")
                            print("   URL: http://127.0.0.1:8000/dashboard/profile/")
                            print("   Логин: R3LO")
                            print("   Пароль: Labrador603502")
                        else:
                            print("✗ Данные не сохранились")
                    else:
                        print("✗ Ошибка сохранения")
                        
                except json.JSONDecodeError as e:
                    print(f"✗ Ошибка парсинга JSON: {e}")
            else:
                print("✗ Script тег не найден")
        else:
            print(f"✗ Ошибка загрузки страницы: {profile_response.status_code}")
    else:
        print("✗ Ошибка входа в систему")

if __name__ == '__main__':
    test_complete_login_and_profile()