#!/usr/bin/env python
"""
Тест HTTP POST запроса для сохранения профиля
"""
import os
import sys
import json

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
sys.path.append('.')

import django
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware

from tlog.views.main import profile_update

def test_profile_post():
    """Тестируем POST запрос к profile_update"""
    
    print("=== ТЕСТ HTTP POST ЗАПРОСА ===")
    
    # Создаем фабрику запросов
    factory = RequestFactory()
    
    # Создаем тестового пользователя
    try:
        user = User.objects.get(username='test_callsign_debug')
        print(f"✓ Пользователь найден: {user.username}")
    except User.DoesNotExist:
        print("✗ Пользователь test_callsign_debug не найден")
        return
    
    # Создаем POST запрос с данными формы
    post_data = {
        'first_name': 'Тест',
        'last_name': 'Пользователь', 
        'qth': 'Москва',
        'my_gridsquare': 'KO85UU',
        'email': 'test@example.com',
        'my_callsigns_json': json.dumps([
            {'name': 'TEST123'},
            {'name': 'UA4LO/AM'},
            {'name': 'RV3LO'}
        ]),
        'use_lotw': 'on',  # чекбокс
        'lotw_user': 'TEST123',
        'lotw_password': 'testpass',
        'csrfmiddlewaretoken': 'test_token'
    }
    
    request = factory.post('/dashboard/profile/', post_data)
    request.user = user
    
    # Добавляем сессию (имитация аутентифицированного пользователя)
    session_middleware = SessionMiddleware(lambda x: None)
    session_middleware.process_request(request)
    request.session.save()
    
    auth_middleware = AuthenticationMiddleware(lambda x: None) 
    auth_middleware.process_request(request)
    
    print(f"✓ Запрос создан для пользователя: {request.user.username}")
    print(f"POST данные: {post_data}")
    
    # Вызываем view
    try:
        response = profile_update(request)
        print(f"✓ View выполнился успешно")
        print(f"Тип ответа: {type(response)}")
        
        # Проверяем, что данные сохранились
        from tlog.models import RadioProfile
        profile = RadioProfile.objects.get(user=user)
        print(f"Позывные после сохранения: {profile.my_callsigns}")
        print(f"LoTW пользователь: {profile.lotw_user}")
        print(f"LoTW проверен: {profile.lotw_chk_pass}")
        
    except Exception as e:
        print(f"✗ Ошибка при выполнении view: {e}")
        import traceback
        traceback.print_exc()

def test_json_parsing():
    """Тестируем парсинг JSON данных"""
    
    print("\n=== ТЕСТ ПАРСИНГА JSON ===")
    
    # Данные как они приходят из формы
    json_string = '[{"name": "TEST123"}, {"name": "UA4LO/AM"}, {"name": "RV3LO"}]'
    
    print(f"JSON строка: {json_string}")
    
    try:
        parsed = json.loads(json_string)
        print(f"✓ Парсинг успешен: {parsed}")
        print(f"Тип данных: {type(parsed)}")
        
        # Проверяем структуру
        for i, item in enumerate(parsed):
            print(f"Позывной {i+1}: {item}")
            if isinstance(item, dict) and 'name' in item:
                print(f"  ✓ Поле name: {item['name']}")
            else:
                print(f"  ✗ Неверная структура: {item}")
                
    except json.JSONDecodeError as e:
        print(f"✗ Ошибка парсинга JSON: {e}")

if __name__ == '__main__':
    test_json_parsing()
    test_profile_post()