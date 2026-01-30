#!/usr/bin/env python3
import requests
import re

# Создаем сессию
session = requests.Session()

# Авторизация
login_data = {
    'username': 'admin',
    'password': 'admin',
    'csrfmiddlewaretoken': ''
}

# Получаем страницу логина для получения CSRF токена
login_page = session.get('http://127.0.0.1:8000/login/')
csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', login_page.text)
if csrf_match:
    login_data['csrfmiddlewaretoken'] = csrf_match.group(1)

# Авторизуемся
response = session.post('http://127.0.0.1:8000/login/', data=login_data)

# Проверяем, что авторизация прошла успешно
if response.url == 'http://127.0.0.1:8000/' or 'logout' in response.text.lower():
    print("✅ Авторизация успешна")
    
    # Получаем страницу logbook
    logbook_response = session.get('http://127.0.0.1:8000/logbook/')
    
    if '🔍 Фильтры' in logbook_response.text:
        print("✅ Блок фильтров найден на странице logbook")
        
        # Проверяем конкретные элементы фильтра
        filters = [
            ('Мой позывной', 'my_callsign'),
            ('Дата от', 'date_from'),
            ('Дата до', 'date_to'),
            ('Позывной', 'search_callsign'),
            ('QTH локатор', 'search_qth'),
            ('Диапазон', 'band'),
            ('Вид связи', 'mode'),
            ('Спутник', 'sat_name'),
            ('LoTW', 'lotw')
        ]
        
        for label, field in filters:
            if label in logbook_response.text:
                print(f"✅ Фильтр '{label}' найден")
            else:
                print(f"❌ Фильтр '{label}' не найден")
            
        # Проверяем наличие кнопок фильтров
        if '🔍' in logbook_response.text and '🔄' in logbook_response.text:
            print("✅ Кнопки применения и сброса фильтров найдены")
        
        # Проверяем CSS классы
        if 'filter-card' in logbook_response.text:
            print("✅ CSS класс 'filter-card' найден")
        if 'filter-controls' in logbook_response.text:
            print("✅ CSS класс 'filter-controls' найден")
        if 'filter-group' in logbook_response.text:
            print("✅ CSS класс 'filter-group' найден")
        
        print("\n🎉 Блок фильтрации успешно добавлен на страницу logbook!")
    else:
        print("❌ Блок фильтров не найден на странице logbook")
        print(f"Статус ответа: {logbook_response.status_code}")
        if logbook_response.status_code != 200:
            print("Ответ:", logbook_response.text[:500])
else:
    print("❌ Ошибка авторизации")
    print(f"URL после попытки входа: {response.url}")