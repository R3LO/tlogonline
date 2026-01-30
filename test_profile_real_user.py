#!/usr/bin/env python
"""
Тест страницы профиля с реальными учетными данными R3LO
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

def test_profile_with_real_user():
    """Тестируем страницу профиля с пользователем R3LO"""
    
    print("=== ТЕСТ СТРАНИЦЫ ПРОФИЛЯ С ПОЛЬЗОВАТЕЛЕМ R3LO ===")
    
    # Получаем пользователя R3LO
    try:
        user = User.objects.get(username='R3LO')
        print(f"✓ Пользователь найден: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Активен: {user.is_active}")
    except User.DoesNotExist:
        print("✗ Пользователь R3LO не найден")
        return
    
    # Получаем профиль
    try:
        profile = RadioProfile.objects.get(user=user)
        print(f"✓ Профиль найден: {profile.callsign}")
        print(f"  Текущие позывные: {profile.my_callsigns}")
    except RadioProfile.DoesNotExist:
        print("✗ Профиль не найден")
        return
    
    # Создаем клиент для тестирования
    client = Client()
    
    # Входим как пользователь R3LO (эмуляция логина)
    client.force_login(user)
    print("✓ Пользователь аутентифицирован")
    
    # 1. Получаем страницу профиля
    print("\n1. ПОЛУЧЕНИЕ СТРАНИЦЫ ПРОФИЛЯ")
    response = client.get('/dashboard/profile/')
    print(f"   Статус ответа: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Страница загружена успешно")
        
        # Проверяем содержимое страницы
        content = response.content.decode('utf-8')
        
        # Ищем скрытое поле с позывными
        import re
        match = re.search(r'<input[^>]*id="my_callsigns_json"[^>]*value=\'([^\']*)\'', content)
        
        if match:
            json_value = match.group(1)
            print(f"✓ Найдены данные в скрытом поле: {json_value}")
            
            try:
                callsigns = json.loads(json_value)
                print(f"✓ Парсинг JSON успешен: {callsigns}")
                
                if len(callsigns) == 0:
                    print("ℹ  Позывных пока нет, добавим тестовые данные")
                    test_callsigns = [
                        {'name': 'R3LO'},
                        {'name': 'R3LO/M'},
                        {'name': 'R3LO/AM'},
                        {'name': 'UA3LO'}
                    ]
                else:
                    print(f"ℹ  Загружено {len(callsigns)} позывных: {callsigns}")
                    test_callsigns = callsigns + [{'name': 'NEW_TEST'}]
                
                # 2. Тестируем сохранение данных
                print(f"\n2. ТЕСТ СОХРАНЕНИЯ ДАННЫХ")
                print(f"   Сохраняем позывные: {test_callsigns}")
                
                post_data = {
                    'first_name': 'Тест',
                    'last_name': 'Пользователь',
                    'qth': 'Москва',
                    'my_gridsquare': 'KO85UU',
                    'email': user.email or 'test@example.com',
                    'my_callsigns_json': json.dumps(test_callsigns),
                    'use_lotw': 'on',
                    'lotw_user': 'R3LO',
                    'lotw_password': 'testpass123',
                    'csrfmiddlewaretoken': 'test_token'  # Для CSRF
                }
                
                # Выполняем POST запрос
                save_response = client.post('/dashboard/profile/', post_data)
                print(f"   Статус сохранения: {save_response.status_code}")
                
                if save_response.status_code in [200, 302]:
                    print("✓ Данные отправлены успешно")
                    
                    # Проверяем данные в базе
                    profile.refresh_from_db()
                    print(f"   Позывные в базе после сохранения: {profile.my_callsigns}")
                    
                    try:
                        # Данные уже распарсены Django, поэтому не нужно json.loads
                        saved_callsigns = profile.my_callsigns
                        print(f"✓ Данные из базы: {saved_callsigns}")
                        
                        if len(saved_callsigns) == len(test_callsigns):
                            print("✓ Количество позывных сохранилось")
                        else:
                            print(f"✗ Количество позывных не сохранилось")
                        
                        if saved_callsigns == test_callsigns:
                            print("✓ Данные сохранились точно")
                        else:
                            print(f"✗ Данные сохранились не точно")
                            print(f"   Ожидалось: {test_callsigns}")
                            print(f"   Получено: {saved_callsigns}")
                            
                    except Exception as e:
                        print(f"✗ Ошибка получения данных: {e}")
                    
                    # 3. Загружаем страницу снова и проверяем загрузку
                    print(f"\n3. ТЕСТ ЗАГРУЗКИ ДАННЫХ")
                    response2 = client.get('/dashboard/profile/')
                    
                    if response2.status_code == 200:
                        print("✓ Страница загружена повторно")
                        
                        content2 = response2.content.decode('utf-8')
                        match2 = re.search(r'<input[^>]*id="my_callsigns_json"[^>]*value=\'([^\']*)\'', content2)
                        
                        if match2:
                            loaded_json = match2.group(1)
                            print(f"   Загруженные данные: {loaded_json}")
                            
                            try:
                                loaded_callsigns = json.loads(loaded_json)
                                print(f"✓ Парсинг загруженных данных: {loaded_callsigns}")
                                
                                if saved_callsigns == loaded_callsigns:
                                    print("✅ ПОЛНЫЙ ЦИКЛ РАБОТАЕТ: Сохранение и загрузка!")
                                else:
                                    print("❌ ОШИБКА: Данные не загрузились корректно")
                                    print(f"   Сохранено: {saved_callsigns}")
                                    print(f"   Загружено: {loaded_callsigns}")
                            except json.JSONDecodeError as e:
                                print(f"✗ Ошибка парсинга загруженных данных: {e}")
                        else:
                            print("✗ Скрытое поле не найдено при повторной загрузке")
                    else:
                        print(f"✗ Ошибка повторной загрузки: {response2.status_code}")
                        
                else:
                    print(f"✗ Ошибка сохранения: {save_response.status_code}")
                    print(f"   Ответ сервера: {save_response.content.decode('utf-8')[:500]}")
                    
            except json.JSONDecodeError as e:
                print(f"✗ Ошибка парсинга JSON из скрытого поля: {e}")
                
        else:
            print("✗ Скрытое поле my_callsigns_json не найдено")
            
    else:
        print(f"✗ Ошибка загрузки страницы: {response.status_code}")
        print(f"   Ответ сервера: {response.content.decode('utf-8')[:500]}")

def test_javascript_formula():
    """Тестируем JavaScript логику загрузки и сохранения"""
    
    print(f"\n=== ТЕСТ JAVASCRIPT ЛОГИКИ ===")
    
    # Тестируем данные в формате базы
    db_data = '[]'  # Пустые позывные у R3LO
    print(f"Данные из базы: {db_data}")
    
    try:
        # Имитируем JavaScript парсинг
        callsigns = json.loads(db_data)
        print(f"JavaScript парсинг: {callsigns}")
        
        # Имитируем добавление позывного
        if not callsigns:
            callsigns = []  # Если пусто, создаем пустой список
        
        callsigns.append({'name': 'R3LO/M'})
        print(f"После добавления позывного: {callsigns}")
        
        # Имитируем сохранение
        json_to_save = json.dumps(callsigns)
        print(f"JSON для сохранения: {json_to_save}")
        
        # Проверяем формат
        if json_to_save == '[{"name":"R3LO/M"}]':
            print("✓ Формат данных корректный для сохранения")
        else:
            print("✗ Формат данных некорректный")
            
    except Exception as e:
        print(f"✗ Ошибка в JavaScript логике: {e}")

if __name__ == '__main__':
    test_profile_with_real_user()
    test_javascript_formula()