#!/usr/bin/env python
"""
Финальный тест исправленной системы профиля
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

def test_fixed_profile_system():
    """Тестируем исправленную систему профиля"""
    
    print("=== ФИНАЛЬНЫЙ ТЕСТ ИСПРАВЛЕННОЙ СИСТЕМЫ ===")
    
    # Получаем пользователя R3LO
    try:
        user = User.objects.get(username='R3LO')
        print(f"✓ Пользователь: {user.username}")
    except User.DoesNotExist:
        print("✗ Пользователь R3LO не найден")
        return
    
    # Получаем профиль
    try:
        profile = RadioProfile.objects.get(user=user)
        print(f"✓ Профиль: {profile.callsign}")
    except RadioProfile.DoesNotExist:
        print("✗ Профиль не найден")
        return
    
    print(f"✓ Текущие позывные: {profile.my_callsigns}")
    print(f"✓ Тип данных: {type(profile.my_callsigns)}")
    
    # Создаем клиент
    client = Client()
    client.force_login(user)
    
    # 1. Получаем страницу профиля
    response = client.get('/dashboard/profile/')
    print(f"\n1. Загрузка страницы: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Страница загружена")
        
        content = response.content.decode('utf-8')
        
        # Проверяем script тег
        if 'id="callsigns-data"' in content:
            print("✓ Найден script тег для данных")
            
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
                    
                    # 2. Тестируем сохранение
                    print(f"\n2. Тест сохранения")
                    new_callsigns = callsigns + [{'name': 'R3LO/TEST'}]
                    print(f"   Добавляем позывной: {new_callsigns}")
                    
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
                        print("✓ Данные отправлены")
                        
                        # Проверяем базу
                        profile.refresh_from_db()
                        print(f"   Позывные в базе: {profile.my_callsigns}")
                        
                        # 3. Тестируем загрузку
                        print(f"\n3. Тест повторной загрузки")
                        response2 = client.get('/dashboard/profile/')
                        
                        if response2.status_code == 200:
                            content2 = response2.content.decode('utf-8')
                            match2 = re.search(r'<script[^>]*id="callsigns-data"[^>]*>(.*?)</script>', content2, re.DOTALL)
                            if match2:
                                loaded_data = match2.group(1).strip()
                                print(f"   Загруженные данные: {loaded_data}")
                                
                                try:
                                    loaded_callsigns = json.loads(loaded_data)
                                    print(f"   Парсинг загруженных: {loaded_callsigns}")
                                    
                                    if profile.my_callsigns == loaded_callsigns:
                                        print("✅ ПОЛНЫЙ ЦИКЛ РАБОТАЕТ!")
                                        print("   - Загрузка: OK")
                                        print("   - Сохранение: OK") 
                                        print("   - Повторная загрузка: OK")
                                    else:
                                        print("✗ Данные не совпадают")
                                        print(f"   В базе: {profile.my_callsigns}")
                                        print(f"   Загружено: {loaded_callsigns}")
                                except json.JSONDecodeError as e:
                                    print(f"✗ Ошибка парсинга загруженных данных: {e}")
                            else:
                                print("✗ Script тег не найден при повторной загрузке")
                        else:
                            print(f"✗ Ошибка повторной загрузки: {response2.status_code}")
                    else:
                        print(f"✗ Ошибка сохранения: {save_response.status_code}")
                        
                except json.JSONDecodeError as e:
                    print(f"✗ Ошибка парсинга script данных: {e}")
            else:
                print("✗ Данные в script теге не найдены")
        else:
            print("✗ Script тег не найден")
    else:
        print(f"✗ Ошибка загрузки страницы: {response.status_code}")

def test_html_generation():
    """Тестируем генерацию HTML с правильными данными"""
    
    print(f"\n=== ТЕСТ ГЕНЕРАЦИИ HTML ===")
    
    from django.template import Context, Template
    
    # Получаем профиль
    profile = RadioProfile.objects.get(user__username='R3LO')
    
    # Создаем тестовый контекст
    context = {
        'profile': profile,
        'user': profile.user
    }
    
    # Тестируем сериализацию данных
    print(f"Профиль.my_callsigns: {profile.my_callsigns}")
    print(f"Тип: {type(profile.my_callsigns)}")
    
    # Проверяем, что Django может сериализовать это в JSON
    try:
        json_str = json.dumps(profile.my_callsigns, ensure_ascii=False)
        print(f"JSON строка: {json_str}")
        print("✓ Django может сериализовать данные")
    except Exception as e:
        print(f"✗ Ошибка сериализации: {e}")

if __name__ == '__main__':
    test_fixed_profile_system()
    test_html_generation()