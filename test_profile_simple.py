#!/usr/bin/env python
"""
Простой тест сохранения и загрузки данных профиля
"""
import os
import sys
import json

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
sys.path.append('.')

import django
django.setup()

from django.contrib.auth.models import User
from tlog.models import RadioProfile

def test_profile_data_operations():
    """Тестируем операции с данными профиля"""
    
    print("=== ТЕСТ ОПЕРАЦИЙ С ДАННЫМИ ПРОФИЛЯ ===")
    
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
    
    print(f"1. Текущие позывные в базе: {profile.my_callsigns}")
    print(f"   Тип данных: {type(profile.my_callsigns)}")
    
    # 2. Тестируем загрузку данных (эмуляция того, что делает JavaScript)
    raw_data = profile.my_callsigns if profile.my_callsigns else '[]'
    print(f"2. Данные для загрузки в форму: {raw_data}")
    
    try:
        # Парсим JSON как это делает JavaScript
        callsigns = json.loads(raw_data)
        print(f"✓ Парсинг JSON: {callsigns}")
        print(f"   Тип: {type(callsigns)}")
        print(f"   Количество: {len(callsigns) if isinstance(callsigns, list) else 'не список'}")
        
        if isinstance(callsigns, list):
            print(f"   Позывные: {callsigns}")
        
    except json.JSONDecodeError as e:
        print(f"✗ Ошибка парсинга JSON: {e}")
        callsigns = []
    
    # 3. Тестируем сохранение новых данных (эмуляция POST запроса)
    new_callsigns = [
        {'name': 'R3LO'},
        {'name': 'UA4LO/AM'},
        {'name': 'RV3LO'},
        {'name': 'TEST123'}
    ]
    
    print(f"3. Тестируем сохранение: {new_callsigns}")
    
    # Сохраняем как это делает Django view
    profile.lotw_lastsync = None
    profile.my_callsigns = json.dumps(new_callsigns)
    profile.save(update_fields=['lotw_lastsync', 'my_callsigns'])
    
    print("✓ Данные сохранены в базу")
    
    # 4. Проверяем сохранение
    profile.refresh_from_db()
    print(f"4. Проверка сохранения: {profile.my_callsigns}")
    
    try:
        saved_callsigns = json.loads(profile.my_callsigns)
        print(f"✓ Парсинг сохраненных данных: {saved_callsigns}")
        print(f"   Количество: {len(saved_callsigns)}")
        print(f"   Данные: {saved_callsigns}")
        
        # Проверяем, что данные сохранились корректно
        if len(saved_callsigns) == len(new_callsigns):
            print("✓ Количество позывных сохранилось")
        else:
            print(f"✗ Количество позывных не сохранилось: {len(saved_callsigns)} != {len(new_callsigns)}")
            
        if saved_callsigns == new_callsigns:
            print("✓ Данные сохранились точно")
        else:
            print(f"✗ Данные не сохранились точно")
            print(f"   Ожидалось: {new_callsigns}")
            print(f"   Получено: {saved_callsigns}")
            
    except json.JSONDecodeError as e:
        print(f"✗ Ошибка парсинга сохраненных данных: {e}")
    
    # 5. Тестируем полный цикл загрузки и сохранения
    print(f"\n5. Тестируем полный цикл:")
    
    # Загружаем данные (имитация JavaScript)
    current_data = profile.my_callsigns
    print(f"   Загрузка из БД: {current_data}")
    
    # Парсим
    try:
        parsed_data = json.loads(current_data)
        print(f"   Парсинг: {parsed_data}")
        
        # Добавляем новый позывной
        parsed_data.append({'name': 'NEW_CALL'})
        print(f"   Добавление позывного: {parsed_data}")
        
        # Сохраняем обратно
        profile.my_callsigns = json.dumps(parsed_data)
        profile.save(update_fields=['my_callsigns'])
        print(f"   Сохранение: {profile.my_callsigns}")
        
        # Проверяем
        profile.refresh_from_db()
        final_data = json.loads(profile.my_callsigns)
        print(f"   Финальная проверка: {final_data}")
        
        if len(final_data) == len(new_callsigns) + 1:
            print("✓ Полный цикл работает корректно!")
        else:
            print(f"✗ Ошибка в полном цикле")
            
    except Exception as e:
        print(f"✗ Ошибка в полном цикле: {e}")

def test_javascript_data_format():
    """Тестируем формат данных, который ожидает JavaScript"""
    
    print(f"\n=== ТЕСТ ФОРМАТА ДАННЫХ ДЛЯ JAVASCRIPT ===")
    
    # Данные как они хранятся в базе
    database_format = '["CALL1", "CALL2"]'
    print(f"Формат в базе: {database_format}")
    
    # Данные как их ожидает JavaScript
    javascript_format = '[{"name": "CALL1"}, {"name": "CALL2"}]'
    print(f"Формат для JavaScript: {javascript_format}")
    
    # Тестируем конвертацию
    try:
        db_data = json.loads(database_format)
        js_data = [{'name': call} for call in db_data]
        converted = json.dumps(js_data)
        print(f"Конвертированные данные: {converted}")
        
        # Проверяем, что это эквивалентно ожидаемому формату
        expected = json.loads(javascript_format)
        if js_data == expected:
            print("✓ Конвертация работает корректно")
        else:
            print("✗ Ошибка конвертации")
            
    except Exception as e:
        print(f"✗ Ошибка конвертации: {e}")

if __name__ == '__main__':
    test_profile_data_operations()
    test_javascript_data_format()
    
    print(f"\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")