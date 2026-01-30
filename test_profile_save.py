#!/usr/bin/env python
"""
Тест сохранения профиля с позывными LoTW
"""
import os
import django
import sys
import json

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
sys.path.append('.')

django.setup()

from django.contrib.auth.models import User
from tlog.models import RadioProfile

def test_profile_update():
    """Тестируем обновление профиля с позывными"""
    
    print("=== ТЕСТ СОХРАНЕНИЯ ПРОФИЛЯ С ПОЗЫВНЫМИ ===")
    
    # Получаем тестового пользователя
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
        profile = RadioProfile.objects.create(user=user)
        print(f"✓ Профиль создан")
    
    print(f"Текущие позывные: {profile.my_callsigns}")
    
    # Тестовые данные для позывных
    test_callsigns = [
        {'name': 'TEST123'},
        {'name': 'UA4LO/AM'}, 
        {'name': 'RV3LO'}
    ]
    
    print(f"Попытка сохранить позывные: {test_callsigns}")
    
    # Сохраняем данные как это делает view
    profile.my_callsigns = test_callsigns
    profile.save()
    
    print("✓ Данные сохранены")
    
    # Проверяем, что сохранилось
    profile.refresh_from_db()
    print(f"Проверка - позывные после сохранения: {profile.my_callsigns}")
    print(f"Тип данных: {type(profile.my_callsigns)}")
    
    # Тестируем JSON сериализацию
    try:
        json_str = json.dumps(profile.my_callsigns)
        print(f"✓ JSON сериализация работает: {json_str}")
        
        # Тестируем десериализацию
        parsed = json.loads(json_str)
        print(f"✓ JSON десериализация работает: {parsed}")
        
    except Exception as e:
        print(f"✗ Ошибка JSON: {e}")
    
    print("\n=== ТЕСТ ФОРМАТА ДАННЫХ ===")
    
    # Тестируем различные форматы данных
    test_formats = [
        # Формат как в базе (list)
        [{'name': 'CALL1'}, {'name': 'CALL2'}],
        
        # Формат как строка JSON
        json.dumps([{'name': 'CALL1'}, {'name': 'CALL2'}]),
        
        # Простой список строк
        ['CALL1', 'CALL2'],
    ]
    
    for i, test_data in enumerate(test_formats):
        print(f"\nТест формата {i+1}: {test_data}")
        print(f"Тип: {type(test_data)}")
        
        try:
            profile.my_callsigns = test_data
            profile.save()
            profile.refresh_from_db()
            print(f"✓ Сохранено и загружено: {profile.my_callsigns}")
            print(f"✓ Тип после загрузки: {type(profile.my_callsigns)}")
        except Exception as e:
            print(f"✗ Ошибка: {e}")
    
    print("\n=== ТЕСТ ЗАВЕРШЕН ===")

if __name__ == '__main__':
    test_profile_update()