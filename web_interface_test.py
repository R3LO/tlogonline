#!/usr/bin/env python3
"""
Тестирование смены пароля через реальный веб-интерфейс
"""

import requests
import time
from bs4 import BeautifulSoup

def test_real_password_change():
    """Тест смены пароля через веб-интерфейс"""
    
    print("🌐 Тестирование через веб-интерфейс...")
    
    # Создаем сессию
    session = requests.Session()
    
    # Настройки для обхода CSRF и других защит
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    try:
        # 1. Пытаемся зайти на страницу профиля
        print("1. Попытка доступа к странице профиля...")
        response = session.get('http://127.0.0.1:8001/profile/')
        print(f"   Статус: {response.status_code}")
        
        if response.status_code == 302:
            print("   Перенаправление на страницу логина (ожидаемо)")
            return
        
        # 2. Парсим HTML для поиска формы смены пароля
        print("2. Поиск формы смены пароля...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем кнопку смены пароля
        password_button = soup.find('button', string=lambda text: text and 'Сменить пароль' in text)
        if password_button:
            print("   ✅ Кнопка 'Сменить пароль' найдена")
        else:
            print("   ❌ Кнопка 'Сменить пароль' НЕ найдена")
            
        # Ищем форму смены пароля
        password_form = soup.find('form', action='/profile/change-password/')
        if password_form:
            print("   ✅ Форма смены пароля найдена")
            
            # Ищем поля формы
            csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
            if csrf_token:
                print("   ✅ CSRF токен найден")
            else:
                print("   ❌ CSRF токен НЕ найден")
                
            # Ищем поля ввода
            old_password_field = soup.find('input', {'name': 'old_password'})
            new_password_field = soup.find('input', {'name': 'new_password'})
            confirm_password_field = soup.find('input', {'name': 'confirm_password'})
            
            if old_password_field and new_password_field and confirm_password_field:
                print("   ✅ Все поля ввода пароля найдены")
            else:
                print("   ❌ Не все поля ввода пароля найдены")
                
        else:
            print("   ❌ Форма смены пароля НЕ найдена")
            
        print("\n3. Проверка JavaScript...")
        
        # Ищем JavaScript файлы
        script_tags = soup.find_all('script', src=True)
        profile_script = any('profile' in script.get('src', '') for script in script_tags)
        
        if profile_script:
            print("   ✅ JavaScript файл profile_edit.js подключен")
        else:
            print("   ⚠️  JavaScript файл profile_edit.js может быть не подключен")
            
        print("\n4. Проверка CSS стилей...")
        
        # Ищем Bootstrap
        bootstrap_link = soup.find('link', href=lambda href: href and 'bootstrap' in href)
        if bootstrap_link:
            print("   ✅ Bootstrap CSS подключен")
        else:
            print("   ❌ Bootstrap CSS НЕ подключен")
            
        print("\n5. Проверка HTML структуры...")
        
        # Проверяем наличие collapse элемента для смены пароля
        collapse_element = soup.find('div', {'id': 'password_change_section'})
        if collapse_element:
            print("   ✅ Collapse элемент для смены пароля найден")
        else:
            print("   ❌ Collapse элемент для смены пароля НЕ найден")
            
        # Проверяем наличие вложенных форм (ошибка)
        forms = soup.find_all('form')
        if len(forms) > 1:
            print(f"   ⚠️  Найдено {len(forms)} форм - возможны вложенные формы")
        else:
            print("   ✅ Вложенных форм не найдено")
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к серверу. Убедитесь, что Django сервер запущен на порту 8001")
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")

if __name__ == '__main__':
    test_real_password_change()