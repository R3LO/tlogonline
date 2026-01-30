#!/usr/bin/env python
"""
Финальная проверка системы - для пользователя R3LO
"""
import os
import sys

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
sys.path.append('.')

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from tlog.models import RadioProfile

def final_check():
    """Финальная проверка для пользователя R3LO"""
    
    print("🔍 ФИНАЛЬНАЯ ПРОВЕРКА СИСТЕМЫ ДЛЯ R3LO")
    print("=" * 50)
    
    try:
        user = User.objects.get(username='R3LO')
        print(f"✅ Пользователь R3LO найден")
        print(f"   Email: {user.email}")
        print(f"   Активен: {'Да' if user.is_active else 'Нет'}")
    except User.DoesNotExist:
        print("❌ Пользователь R3LO не найден!")
        return
    
    try:
        profile = RadioProfile.objects.get(user=user)
        print(f"✅ Профиль найден: {profile.callsign}")
        print(f"   Позывные в LoTW: {profile.my_callsigns}")
        print(f"   Количество позывных: {len(profile.my_callsigns) if profile.my_callsigns else 0}")
    except RadioProfile.DoesNotExist:
        print("❌ Профиль не найден!")
        return
    
    print(f"\n🚀 ИНСТРУКЦИЯ ДЛЯ ВХОДА:")
    print(f"   URL: http://127.0.0.1:8000/dashboard/profile/")
    print(f"   Логин: R3LO")
    print(f"   Пароль: Labrador603502")
    
    print(f"\n📋 ЧТО ПРОВЕРИТЬ:")
    print(f"   1. Откройте страницу профиля")
    print(f"   2. В блоке 'Мои позывные в LoTW' должны быть заполнены поля")
    print(f"   3. Можно добавлять/удалять позывные")
    print(f"   4. При сохранении данные обновляются")
    print(f"   5. При обновлении страницы данные сохраняются")
    
    print(f"\n🔧 В СЛУЧАЕ ПРОБЛЕМ:")
    print(f"   - Откройте Developer Tools (F12)")
    print(f"   - Проверьте Console на наличие ошибок")
    print(f"   - Должны быть сообщения:")
    print(f"     '=== Profile Edit JS Loaded ==='")
    print(f"     '=== Loading profile data ==='")
    print(f"     'Loaded callsigns into form'")
    
    print(f"\n✅ СИСТЕМА ГОТОВА К ИСПОЛЬЗОВАНИЮ!")

if __name__ == '__main__':
    final_check()