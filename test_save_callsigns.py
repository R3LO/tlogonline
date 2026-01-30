#!/usr/bin/env python3
"""
Простой тест для проверки сохранения позывных
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tlogonline.settings')
sys.path.append('/home/vlad/tlogonline')

django.setup()

from tlog.models import RadioProfile
from django.contrib.auth.models import User
import json

def test_save_callsigns():
    print("=== Тест сохранения позывных ===\n")
    
    # Создаём или получаем тестового пользователя
    user = User.objects.get(username='test_callsign_debug')
    profile = user.radio_profile
    
    print(f"Пользователь: {user.username}")
    print(f"Текущие позывные в профиле: {profile.my_callsigns}")
    
    # Тестовые данные для сохранения
    test_callsigns = [
        {'name': 'R3LO'},
        {'name': 'TEST123'},
        {'name': 'UA4LO/AM'},
        {'name': 'RV3LO'}
    ]
    
    print(f"\nСохраняем новые данные: {test_callsigns}")
    
    # Сохраняем данные
    profile.my_callsigns = test_callsigns
    profile.save()
    
    print("Данные сохранены")
    
    # Проверяем, что данные сохранились
    profile.refresh_from_db()
    print(f"Проверяем после сохранения: {profile.my_callsigns}")
    print(f"Тип данных: {type(profile.my_callsigns)}")
    
    # Тест сериализации для шаблона
    json_data = json.dumps(profile.my_callsigns)
    print(f"\nJSON для шаблона: {json_data}")
    
    # Тест парсинга
    try:
        parsed = json.loads(json_data)
        print(f"Парсинг прошёл успешно: {parsed}")
        print(f"Данные совпадают: {parsed == test_callsigns}")
    except Exception as e:
        print(f"Ошибка парсинга: {e}")
    
    print("\n=== Тест завершён ===")

if __name__ == "__main__":
    test_save_callsigns()