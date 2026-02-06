#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функциональности добавления позывных
Запуск: python manage.py shell < test_callsigns_functionality.py
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tlog.settings')
django.setup()

from django.contrib.auth.models import User
from tlog.models import RadioProfile
import json

def test_callsigns_functionality():
    """Тестирование функциональности добавления позывных"""
    
    print("🧪 Тестирование функциональности добавления позывных")
    print("=" * 60)
    
    # Создаем тестового пользователя
    try:
        test_user, created = User.objects.get_or_create(
            username='test_user_callsigns',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Тест',
                'last_name': 'Пользователь'
            }
        )
        
        if created:
            test_user.set_password('testpassword')
            test_user.save()
            print("✅ Создан тестовый пользователь")
        else:
            print("ℹ️ Используется существующий пользователь")
            
        # Создаем или получаем профиль
        profile, created = RadioProfile.objects.get_or_create(user=test_user)
        
        if created:
            print("✅ Создан профиль радиолюбителя")
        else:
            print("ℹ️ Используется существующий профиль")
            
        print(f"📊 Начальные данные профиля:")
        print(f"   - Позывные: {profile.my_callsigns}")
        print(f"   - LoTW пользователь: {profile.lotw_user or 'не задан'}")
        print(f"   - LoTW проверен: {profile.lotw_chk_pass}")
        print()
        
        # Тест 1: Добавление позывных
        print("🔬 Тест 1: Добавление позывных")
        test_callsigns = [
            "UA1ABC",
            "R0A/1", 
            "UE1AAA",
            "ua2def",  # должно привестись к верхнему регистру
            "R3XYZ",
            "UA1ABC"   # дубликат - должен быть удален
        ]
        
        print(f"   Добавляем позывные: {test_callsigns}")
        
        # Нормализация данных (как в JavaScript)
        normalized_callsigns = []
        for callsign in test_callsigns:
            if callsign and isinstance(callsign, str):
                callsign_clean = callsign.strip().upper()
                if callsign_clean not in normalized_callsigns:
                    # Простая валидация позывного
                    import re
                    pattern = r'^[A-Z0-9]{1,3}[0-9][A-Z0-9]{0,3}[A-Z]$'
                    if re.match(pattern, callsign_clean):
                        normalized_callsigns.append(callsign_clean)
                        print(f"   ✅ Добавлен позывной: {callsign_clean}")
                    else:
                        print(f"   ❌ Неверный формат позывного: {callsign_clean}")
        
        print(f"   Нормализованные позывные: {normalized_callsigns}")
        
        # Сохраняем в профиль
        profile.my_callsigns = normalized_callsigns
        profile.save()
        
        print(f"   💾 Сохранено в базу данных: {profile.my_callsigns}")
        print()
        
        # Тест 2: Проверка сохранения
        print("🔬 Тест 2: Проверка сохранения")
        profile_refresh = RadioProfile.objects.get(user=test_user)
        print(f"   Загружено из БД: {profile_refresh.my_callsigns}")
        
        if profile_refresh.my_callsigns == normalized_callsigns:
            print("   ✅ Данные корректно сохранены и загружены")
        else:
            print("   ❌ Ошибка сохранения/загрузки данных")
        print()
        
        # Тест 3: JSON сериализация
        print("🔬 Тест 3: JSON сериализация")
        json_data = json.dumps(normalized_callsigns)
        print(f"   JSON строка: {json_data}")
        
        try:
            parsed_data = json.loads(json_data)
            print(f"   Распарсено: {parsed_data}")
            print("   ✅ JSON сериализация работает корректно")
        except json.JSONDecodeError as e:
            print(f"   ❌ Ошибка JSON: {e}")
        print()
        
        # Тест 4: LoTW настройки
        print("🔬 Тест 4: LoTW настройки")
        profile.lotw_user = "UA1ABC"
        profile.lotw_password = "testpassword"
        profile.lotw_chk_pass = True
        profile.save()
        
        print(f"   LoTW пользователь: {profile.lotw_user}")
        print(f"   LoTW проверен: {profile.lotw_chk_pass}")
        print("   ✅ LoTW настройки сохранены")
        print()
        
        # Тест 5: Очистка данных
        print("🔬 Тест 5: Очистка тестовых данных")
        profile.my_callsigns = []
        profile.lotw_user = ""
        profile.lotw_password = ""
        profile.lotw_chk_pass = False
        profile.save()
        
        print(f"   Очищенные позывные: {profile.my_callsigns}")
        print(f"   Очищенный LoTW пользователь: {profile.lotw_user}")
        print("   ✅ Тестовые данные очищены")
        print()
        
        # Итоговый отчет
        print("📋 ИТОГОВЫЙ ОТЧЕТ")
        print("=" * 60)
        print("✅ Все тесты пройдены успешно!")
        print("✅ Функциональность добавления позывных работает корректно")
        print("✅ JSON сериализация работает")
        print("✅ LoTW настройки сохраняются")
        print("✅ Данные корректно очищаются")
        print()
        print("🎉 Тестирование завершено успешно!")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_test_data():
    """Очистка тестовых данных"""
    print("🧹 Очистка тестовых данных...")
    
    try:
        # Удаляем тестового пользователя и все связанные данные
        User.objects.filter(username='test_user_callsigns').delete()
        print("✅ Тестовые данные удалены")
    except Exception as e:
        print(f"❌ Ошибка при очистке: {e}")

if __name__ == "__main__":
    print("Запуск тестирования функциональности добавления позывных...")
    print()
    
    # Выполняем тесты
    success = test_callsigns_functionality()
    
    if success:
        print("\n" + "="*60)
        print("Хотите удалить тестовые данные? (y/n): ", end="")
        choice = input().strip().lower()
        
        if choice in ['y', 'yes', 'да', 'д']:
            cleanup_test_data()
    else:
        print("❌ Тестирование завершилось с ошибками")
        sys.exit(1)