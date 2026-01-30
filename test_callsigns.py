#!/usr/bin/env python3
"""
Простой тест для проверки загрузки и сохранения позывных
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
sys.path.append('.')

django.setup()

from tlog.models import RadioProfile
from django.contrib.auth.models import User
import json

def test_callsigns():
    print("=== Тест загрузки и сохранения позывных ===\n")
    
    # Создаём или получаем тестового пользователя
    user, created = User.objects.get_or_create(username='test_callsign_debug')
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Создан новый пользователь: {user.username}")
    
    # Создаём или получаем профиль
    profile, created = RadioProfile.objects.get_or_create(user=user)
    
    print(f"Профиль пользователя: {profile.user.username}")
    print(f"Существующие my_callsigns: {profile.my_callsigns}")
    print(f"Тип данных: {type(profile.my_callsigns)}")
    
    # Тестовые данные
    test_callsigns = [
        {'name': 'TEST1'},
        {'name': 'TEST2'},
        {'name': 'TEST3/AM'}
    ]
    
    print(f"\nТестовые данные для сохранения: {test_callsigns}")
    
    # Сохраняем данные
    profile.my_callsigns = test_callsigns
    profile.save()
    
    print(f"Данные сохранены в профиль")
    
    # Загружаем данные из базы
    profile.refresh_from_db()
    
    print(f"Загруженные данные: {profile.my_callsigns}")
    print(f"Тип загруженных данных: {type(profile.my_callsigns)}")
    
    # Проверяем, что данные одинаковые
    if profile.my_callsigns == test_callsigns:
        print("✅ Тест пройден: данные сохранились и загрузились корректно")
    else:
        print("❌ Тест провален: данные не совпадают")
        print(f"Ожидалось: {test_callsigns}")
        print(f"Получено: {profile.my_callsigns}")
    
    # Тест сериализации в JSON
    print(f"\n=== Тест сериализации JSON ===")
    
    try:
        json_data = json.dumps(profile.my_callsigns)
        print(f"JSON сериализация: {json_data}")
        
        parsed_data = json.loads(json_data)
        print(f"JSON десериализация: {parsed_data}")
        
        if parsed_data == test_callsigns:
            print("✅ JSON тест пройден")
        else:
            print("❌ JSON тест провален")
            
    except Exception as e:
        print(f"❌ Ошибка JSON: {e}")
    
    # Тест Django шаблонизатора
    print(f"\n=== Тест Django шаблонизатора ===")
    
    from django.template.defaultfilters import escapejs
    
    json_for_template = escapejs(json_data)
    print(f"JSON для шаблона: {json_for_template}")
    
    # Проверяем, что escapejs работает правильно
    if '"name"' in json_for_template:
        print("✅ Django escapejs работает корректно")
    else:
        print("❌ Проблема с Django escapejs")
    
    print(f"\n=== Завершение теста ===")
    
if __name__ == "__main__":
    test_callsigns()