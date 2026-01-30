#!/usr/bin/env python
"""
Тест страницы профиля с аутентификацией
"""
import os
import sys
import json

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
sys.path.append('.')

import django
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from tlog.models import RadioProfile

def test_profile_page():
    """Тестируем страницу профиля с аутентификацией"""
    
    print("=== ТЕСТ СТРАНИЦЫ ПРОФИЛЯ ===")
    
    # Получаем пользователя
    try:
        user = User.objects.get(username='test_callsign_debug')
        print(f"✓ Пользователь найден: {user.username}")
    except User.DoesNotExist:
        print("✗ Пользователь test_callsign_debug не найден")
        return
    
    # Получаем или создаем профиль
    try:
        profile = RadioProfile.objects.get(user=user)
        print(f"✓ Профиль найден")
    except RadioProfile.DoesNotExist:
        profile = RadioProfile.objects.create(user=user, callsign='TEST123')
        print(f"✓ Профиль создан")
    
    print(f"Текущие позывные в базе: {profile.my_callsigns}")
    
    # Создаем клиент для тестирования
    client = Client()
    
    # Входим как пользователь
    client.force_login(user)
    print("✓ Пользователь аутентифицирован")
    
    # Получаем страницу профиля
    response = client.get('/dashboard/profile/')
    print(f"✓ GET запрос выполнен, статус: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Страница профиля загружена успешно")
        
        # Проверяем, что в контенте есть наши позывные
        content = response.content.decode('utf-8')
        if 'my_callsigns_json' in content:
            print("✓ Найдено скрытое поле my_callsigns_json")
            
            # Извлекаем данные из скрытого поля
            import re
            match = re.search(r'<input[^>]*id="my_callsigns_json"[^>]*value=\'([^\']*)\'', content)
            if match:
                json_value = match.group(1)
                print(f"✓ Данные из скрытого поля: {json_value}")
                
                try:
                    callsigns = json.loads(json_value)
                    print(f"✓ Парсинг JSON: {callsigns}")
                    
                    # Создаем тестовые данные для сохранения
                    test_callsigns = [
                        {'name': 'TEST123'},
                        {'name': 'UA4LO/AM'},
                        {'name': 'RV3LO'}
                    ]
                    
                    print(f"\nТестируем сохранение позывных: {test_callsigns}")
                    
                    # Создаем POST запрос
                    post_data = {
                        'first_name': 'Тест',
                        'last_name': 'Пользователь',
                        'qth': 'Москва',
                        'my_gridsquare': 'KO85UU',
                        'email': 'test@example.com',
                        'my_callsigns_json': json.dumps(test_callsigns),
                        'use_lotw': 'on',
                        'lotw_user': 'TEST123',
                        'lotw_password': 'testpass',
                    }
                    
                    save_response = client.post('/dashboard/profile/', post_data)
                    print(f"✓ POST запрос выполнен, статус: {save_response.status_code}")
                    
                    if save_response.status_code in [200, 302]:
                        print("✓ Данные сохранены успешно")
                        
                        # Проверяем, что данные сохранились в базе
                        profile.refresh_from_db()
                        print(f"✓ Позывные в базе после сохранения: {profile.my_callsigns}")
                        
                        # Проверяем, что данные изменились
                        try:
                            new_callsigns = json.loads(profile.my_callsigns)
                            if len(new_callsigns) == 3:
                                print("✓ Количество позывных правильное")
                            else:
                                print(f"✗ Количество позывных неправильное: {len(new_callsigns)}")
                                
                            print(f"✓ Сохраненные позывные: {new_callsigns}")
                        except json.JSONDecodeError:
                            print("✗ Ошибка парсинга сохраненных данных")
                    else:
                        print(f"✗ Ошибка сохранения: {save_response.status_code}")
                        
                except json.JSONDecodeError as e:
                    print(f"✗ Ошибка парсинга JSON: {e}")
            else:
                print("✗ Скрытое поле my_callsigns_json не найдено")
        else:
            print("✗ Скрытое поле my_callsigns_json не найдено в контенте")
    else:
        print(f"✗ Ошибка загрузки страницы: {response.status_code}")

def test_complete_workflow():
    """Тестируем полный рабочий процесс"""
    
    print("\n=== ТЕСТ ПОЛНОГО РАБОЧЕГО ПРОЦЕССА ===")
    
    # Получаем пользователя
    user = User.objects.get(username='test_callsign_debug')
    
    # Создаем клиент
    client = Client()
    client.force_login(user)
    
    # 1. Загружаем страницу и проверяем начальные данные
    response = client.get('/dashboard/profile/')
    content = response.content.decode('utf-8')
    
    # Извлекаем данные из скрытого поля
    import re
    match = re.search(r'<input[^>]*id="my_callsigns_json"[^>]*value=\'([^\']*)\'', content)
    initial_json = match.group(1) if match else '[]'
    
    print(f"1. Начальные данные: {initial_json}")
    
    # 2. Подготавливаем новые данные
    new_callsigns = [
        {'name': 'R3LO'},
        {'name': 'UA4LO/AM'},
        {'name': 'RV3LO'},
        {'name': 'TEST123'}
    ]
    new_json = json.dumps(new_callsigns)
    
    print(f"2. Новые данные: {new_json}")
    
    # 3. Сохраняем данные
    post_data = {
        'first_name': 'Тест',
        'last_name': 'Пользователь', 
        'qth': 'Москва',
        'my_gridsquare': 'KO85UU',
        'email': 'test@example.com',
        'my_callsigns_json': new_json,
        'use_lotw': 'on',
        'lotw_user': 'R3LO',
        'lotw_password': 'testpass',
    }
    
    save_response = client.post('/dashboard/profile/', post_data)
    print(f"3. Сохранение: статус {save_response.status_code}")
    
    # 4. Проверяем данные в базе
    profile = RadioProfile.objects.get(user=user)
    print(f"4. Данные в базе: {profile.my_callsigns}")
    
    # 5. Загружаем страницу снова и проверяем, что данные загрузились
    response2 = client.get('/dashboard/profile/')
    content2 = response2.content.decode('utf-8')
    match2 = re.search(r'<input[^>]*id="my_callsigns_json"[^>]*value=\'([^\']*)\'', content2)
    loaded_json = match2.group(1) if match2 else '[]'
    
    print(f"5. Загруженные данные: {loaded_json}")
    
    # 6. Проверяем, что данные совпадают
    if new_json == loaded_json:
        print("✅ ПОЛНЫЙ ЦИКЛ РАБОТАЕТ: Данные сохраняются и загружаются корректно!")
    else:
        print("❌ ОШИБКА: Данные не сохранились или не загрузились корректно")
        print(f"Ожидалось: {new_json}")
        print(f"Получено: {loaded_json}")

if __name__ == '__main__':
    test_profile_page()
    test_complete_workflow()