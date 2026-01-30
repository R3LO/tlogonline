#!/usr/bin/env python
"""
Простой тест обработки данных в profile_update
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

def test_profile_update_logic():
    """Тестируем логику обновления профиля как в view"""
    
    print("=== ТЕСТ ЛОГИКИ profile_update ===")
    
    # Получаем пользователя
    try:
        user = User.objects.get(username='test_callsign_debug')
        print(f"✓ Пользователь: {user.username}")
    except User.DoesNotExist:
        print("✗ Пользователь не найден")
        return
    
    # Получаем профиль
    try:
        profile = RadioProfile.objects.get(user=user)
        print(f"✓ Профиль найден")
    except RadioProfile.DoesNotExist:
        profile = RadioProfile.objects.create(user=user)
        print(f"✓ Профиль создан")
    
    print(f"Исходные позывные: {profile.my_callsigns}")
    
    # Имитируем данные POST запроса
    my_callsigns_json = '[{"name": "TEST123"}, {"name": "UA4LO/AM"}, {"name": "RV3LO"}]'
    
    print(f"Получен my_callsigns_json: {my_callsigns_json}")
    
    # Выполняем ту же логику что и в view
    try:
        new_my_callsigns = json.loads(my_callsigns_json)
        print(f"✓ Парсинг JSON успешен: {new_my_callsigns}")
        print(f"Тип данных: {type(new_my_callsigns)}")
    except json.JSONDecodeError as e:
        new_my_callsigns = []
        print(f"✗ Ошибка парсинга JSON: {e}")
    
    # Проверяем старые данные
    old_my_callsigns = profile.my_callsigns if profile.my_callsigns else []
    print(f"Старые позывные из БД: {old_my_callsigns}")
    print(f"Тип старых данных: {type(old_my_callsigns)}")
    
    # Проверяем, изменились ли данные
    if isinstance(old_my_callsigns, str):
        try:
            old_my_callsigns = json.loads(old_my_callsigns)
            print(f"Конвертировали старые данные из строки: {old_my_callsigns}")
        except json.JSONDecodeError:
            old_my_callsigns = []
            print("Не удалось распарсить старые данные как JSON")
    
    print(f"Сравнение:")
    print(f"  Старые: {old_my_callsigns}")
    print(f"  Новые:  {new_my_callsigns}")
    print(f"  Равны:  {old_my_callsigns == new_my_callsigns}")
    
    # Сохраняем данные (как в view)
    if old_my_callsigns != new_my_callsigns:
        profile.lotw_lastsync = None
        profile.my_callsigns = new_my_callsigns
        profile.save(update_fields=['lotw_lastsync', 'my_callsigns'])
        print("✓ Сохранено с сбросом lotw_lastsync")
    else:
        profile.my_callsigns = new_my_callsigns
        profile.save(update_fields=['my_callsigns'])
        print("✓ Сохранено без изменений lotw_lastsync")
    
    # Проверяем результат
    profile.refresh_from_db()
    print(f"Позывные после сохранения: {profile.my_callsigns}")
    print(f"Тип после сохранения: {type(profile.my_callsigns)}")
    print(f"lotw_lastsync: {profile.lotw_lastsync}")
    
    # Тестируем разные форматы данных
    print("\n=== ТЕСТ РАЗНЫХ ФОРМАТОВ ===")
    
    test_cases = [
        ("Список словарей", [{'name': 'CALL1'}, {'name': 'CALL2'}]),
        ("JSON строка", json.dumps([{'name': 'CALL1'}, {'name': 'CALL2'}])),
        ("Простой список", ['CALL1', 'CALL2']),
        ("JSON простой список", json.dumps(['CALL1', 'CALL2'])),
    ]
    
    for name, test_data in test_cases:
        print(f"\nТест: {name}")
        print(f"Данные: {test_data}")
        print(f"Тип: {type(test_data)}")
        
        try:
            # Сохраняем
            profile.my_callsigns = test_data
            profile.save()
            
            # Загружаем
            profile.refresh_from_db()
            result = profile.my_callsigns
            
            print(f"Результат: {result}")
            print(f"Тип результата: {type(result)}")
            print(f"✓ Успех")
            
        except Exception as e:
            print(f"✗ Ошибка: {e}")

if __name__ == '__main__':
    test_profile_update_logic()