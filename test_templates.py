#!/usr/bin/env python
"""
Простой тест для проверки загрузки шаблонов
"""
import os
import sys
import django
from django.conf import settings

# Настройка Django
sys.path.insert(0, '/home/vlad/tlogonline')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.template import loader, Template, Context

def test_templates():
    """Тестирование загрузки шаблонов"""
    
    print("=== Тестирование загрузки шаблонов ===")
    
    # Проверяем загрузку base.html
    try:
        base_template = loader.get_template('base.html')
        print("✅ base.html загружен успешно")
    except Exception as e:
        print(f"❌ Ошибка загрузки base.html: {e}")
    
    # Проверяем загрузку base_dashboard.html
    try:
        dashboard_template = loader.get_template('base_dashboard.html')
        print("✅ base_dashboard.html загружен успешно")
    except Exception as e:
        print(f"❌ Ошибка загрузки base_dashboard.html: {e}")
    
    # Проверяем загрузку dashboard.html
    try:
        dashboard_main_template = loader.get_template('dashboard.html')
        print("✅ dashboard.html загружен успешно")
    except Exception as e:
        print(f"❌ Ошибка загрузки dashboard.html: {e}")
    
    # Проверяем загрузку qo100/base.html
    try:
        qo100_template = loader.get_template('qo100/base.html')
        print("✅ qo100/base.html загружен успешно")
    except Exception as e:
        print(f"❌ Ошибка загрузки qo100/base.html: {e}")
    
    # Дополнительно проверим исходный код шаблонов через loader
    print("\n=== Проверка исходного кода шаблонов ===")
    try:
        base_source = loader.get_template('base.html').engine.get_template('base.html').source
        print(f"base.html первые 200 символов: {base_source[:200]}...")
    except:
        print("Не удалось получить исходный код base.html")
        
    try:
        dashboard_source = loader.get_template('dashboard.html').engine.get_template('dashboard.html').source
        print(f"dashboard.html первые 200 символов: {dashboard_source[:200]}...")
    except:
        print("Не удалось получить исходный код dashboard.html")
    
    print("\n=== Тестирование рендеринга ===")
    
    # Тестируем рендеринг dashboard.html с минимальным контекстом
    try:
        context = {
            'user': None,
            'LANGUAGE_CODE': 'ru',
            'LANGUAGES': [('ru', 'Русский'), ('en', 'English')],
            'messages': []
        }
        
        dashboard_main_template = loader.get_template('dashboard.html')
        rendered = dashboard_main_template.render(context)
        print("✅ dashboard.html отрендерен успешно")
        print(f"   Размер рендера: {len(rendered)} символов")
        
        # Проверяем, что используется правильный базовый шаблон
        if 'class="navbar navbar-expand-lg navbar-dark bg-dark"' in rendered:
            print("✅ Используется правильная навигация (base.html)")
        else:
            print("❌ Навигация не найдена или неправильная")
            
        if 'dashboard_content' in rendered:
            print("✅ Используется правильный блок dashboard_content")
        else:
            print("❌ Блок dashboard_content не найден")
            
        # Проверяем наличие QO-100 навигации (которая не должна быть)
        if '📡 QO-100 Рейтинг' in rendered:
            print("❌ Обнаружена QO-100 навигация (неправильно)")
        else:
            print("✅ QO-100 навигация отсутствует (правильно)")
            
        # Проверяем наличие основного контента dashboard
        if '📊 Profile' in rendered:
            print("✅ Найден заголовок Profile (правильно)")
        else:
            print("❌ Заголовок Profile не найден")
            
        # Проверяем наличие элементов фильтров
        if 'filter_my_callsign' in rendered:
            print("✅ Найдены элементы фильтров (правильно)")
        else:
            print("❌ Элементы фильтров не найдены")
            
    except Exception as e:
        print(f"❌ Ошибка рендеринга dashboard.html: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_templates()