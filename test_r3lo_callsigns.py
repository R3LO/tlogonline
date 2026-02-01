#!/usr/bin/env python3
"""
Тест загрузки позывных для пользователя R3LO
"""
import requests
import json
from bs4 import BeautifulSoup

# Настройки
BASE_URL = "http://127.0.0.1:8000"
USERNAME = "R3LO"
PASSWORD = "Labrador603502"

def test_lotw_callsigns():
    """Тестирование загрузки позывных для пользователя R3LO"""
    
    session = requests.Session()
    
    print("🔐 Вход в систему...")
    
    # Получаем страницу логина для получения CSRF токена
    login_page = session.get(f"{BASE_URL}/accounts/login/")
    soup = BeautifulSoup(login_page.content, 'html.parser')
    
    # Ищем CSRF токен разными способами
    csrf_token = None
    csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if csrf_input:
        csrf_token = csrf_input.get('value')
    else:
        # Альтернативный поиск
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        if csrf_input:
            csrf_token = csrf_input.get('value')
        else:
            # Ищем в meta тегах
            csrf_meta = soup.find('meta', {'name': 'csrf-token'})
            if csrf_meta:
                csrf_token = csrf_meta.get('content')
    
    if not csrf_token:
        print("❌ CSRF токен не найден на странице логина")
        print(f"   Status: {login_page.status_code}")
        print(f"   URL: {login_page.url}")
        # Показываем первые 500 символов содержимого для отладки
        print(f"   Content preview: {login_page.text[:500]}...")
        return
    
    # Входим в систему
    login_data = {
        'username': USERNAME,
        'password': PASSWORD,
        'csrfmiddlewaretoken': csrf_token
    }
    
    login_response = session.post(f"{BASE_URL}/accounts/login/", data=login_data)
    
    if login_response.status_code == 200 and f"dashboard/profile/" in login_response.url:
        print("✅ Успешный вход в систему!")
        
        # Получаем CSRF токен для LoTW страницы
        lotw_page = session.get(f"{BASE_URL}/lotw/")
        lotw_soup = BeautifulSoup(lotw_page.content, 'html.parser')
        lotw_csrf = lotw_soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
        
        # Тестируем API загрузки позывных
        print("\n📡 Тестируем API загрузки позывных...")
        
        callsigns_response = session.get(f"{BASE_URL}/api/lotw/callsigns/")
        
        if callsigns_response.status_code == 200:
            callsigns_data = callsigns_response.json()
            
            if callsigns_data.get('success'):
                callsigns = callsigns_data.get('callsigns', [])
                debug_info = callsigns_data.get('debug_info', {})
                
                print(f"✅ API работает! Найдено {len(callsigns)} позывных:")
                for i, callsign in enumerate(callsigns, 1):
                    print(f"  {i}. {callsign}")
                
                if debug_info:
                    print(f"\n📊 Debug информация:")
                    for key, value in debug_info.items():
                        print(f"  {key}: {value}")
                
                # Тестируем фильтрацию
                print(f"\n🔍 Тестируем фильтрацию LoTW...")
                
                filter_data = {
                    'my_callsign': '',
                    'search_callsign': '',
                    'search_qth': '',
                    'band': '',
                    'mode': '',
                    'sat_name': '',
                    'page': 1
                }
                
                filter_response = session.post(
                    f"{BASE_URL}/api/lotw/filter/",
                    headers={'Content-Type': 'application/json'},
                    json=filter_data
                )
                
                if filter_response.status_code == 200:
                    filter_result = filter_response.json()
                    
                    if filter_result.get('success'):
                        total_count = filter_result.get('total_count', 0)
                        qso_data = filter_result.get('qso_data', [])
                        
                        print(f"✅ Фильтрация работает!")
                        print(f"  Всего LoTW записей: {total_count}")
                        print(f"  На этой странице: {len(qso_data)}")
                        
                        if qso_data:
                            print(f"\n📋 Первые {min(3, len(qso_data))} записи:")
                            for i, qso in enumerate(qso_data[:3], 1):
                                print(f"  {i}. {qso.get('date')} {qso.get('time')} - {qso.get('my_callsign')} -> {qso.get('callsign')} ({qso.get('band')}, {qso.get('mode')})")
                    else:
                        print(f"❌ Ошибка фильтрации: {filter_result.get('error')}")
                else:
                    print(f"❌ Ошибка запроса фильтрации: {filter_response.status_code}")
                    
            else:
                print(f"❌ API вернул ошибку: {callsigns_data.get('error')}")
        else:
            print(f"❌ Ошибка API позывных: {callsigns_response.status_code}")
            
    else:
        print("❌ Ошибка входа в систему")
        print(f"   Status: {login_response.status_code}")
        print(f"   URL: {login_response.url}")
        
        # Проверяем, есть ли сообщение об ошибке
        if login_response.status_code == 200:
            error_soup = BeautifulSoup(login_response.content, 'html.parser')
            errors = error_soup.find_all('li', class_='errorlist')
            if errors:
                print("   Ошибки:")
                for error in errors:
                    print(f"   - {error.get_text()}")

if __name__ == "__main__":
    test_lotw_callsigns()