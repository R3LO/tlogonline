# REST API Documentation

## Обзор

REST API позволяет внешним приложениям получать и модифицировать данные из базы данных через HTTP запросы с использованием **Basic Authentication**.

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Запустите сервер:
```bash
python manage.py runserver
```

## Аутентификация

API использует **Basic Authentication**. Каждый запрос должен содержать заголовок `Authorization`:

```
Authorization: Basic base64(username:password)
```

### Пример заголовка:

Для пользователя `testuser` с паролем `testpass`:
- Кодируем в Base64: `testuser:testpass` → `dGVzdHVzZXI6dGVzdHBhc3M=`
- Заголовок: `Authorization: Basic dGVzdHVzZXI6dGVzdHBhc3M=`

## API Endpoints

### 1. Информация о пользователе

**GET** `/api/v1/user-info/`

Получает базовую информацию о текущем авторизованном пользователе.

**Пример запроса:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/user-info/" \
  -H "Authorization: Basic dGVzdHVzZXI6dGVzdHBhc3M="
```

**Пример ответа:**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "first_name": "Test",
  "last_name": "User",
  "date_joined": "2025-01-01T00:00:00Z"
}
```

---

### 2. Профиль пользователя

**GET** `/api/v1/profile/`

Получает профиль радиолюбителя текущего пользователя.

**Пример запроса:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/profile/" \
  -H "Authorization: Basic dGVzdHVzZXI6dGVzdHBhc3M="
```

**Пример ответа:**
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "first_name": "Test",
  "last_name": "User",
  "callsign": "UA0AAA",
  "qth": "Moscow",
  "my_gridsquare": "KN88",
  "lotw_user": "lotw_login",
  "lotw_chk_pass": true,
  "my_callsigns": ["UA0AAA", "UA0AAA/P"],
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-15T12:00:00Z"
}
```

**PATCH** `/api/v1/profile/`

Обновляет профиль пользователя (частичное обновление).

**Пример запроса:**
```bash
curl -X PATCH "http://127.0.0.1:8000/api/v1/profile/" \
  -H "Authorization: Basic dGVzdHVzZXI6dGVzdHBhc3M=" \
  -H "Content-Type: application/json" \
  -d '{
    "callsign": "UA0AAA",
    "qth": "Moscow",
    "my_gridsquare": "KN88"
  }'
```

---

### 3. Список QSO

**GET** `/api/v1/qsos/`

Получает список всех QSO текущего пользователя (с пагинацией).

**Пример запроса:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/qsos/" \
  -H "Authorization: Basic dGVzdHVzZXI6dGVzdHBhc3M="
```

**Пример ответа:**
```json
{
  "count": 150,
  "next": "http://127.0.0.1:8000/api/v1/qsos/?page=2",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "date": "2025-01-15",
      "time": "14:30:00",
      "my_callsign": "UA0AAA",
      "callsign": "UA0BBB",
      "frequency": 14.070,
      "band": "20M",
      "mode": "FT8",
      "rst_sent": "599",
      "rst_rcvd": "599",
      "my_gridsquare": "KN88",
      "gridsquare": "KO85",
      "continent": "EU",
      "state": "",
      "prop_mode": "",
      "sat_name": "",
      "r150s": "",
      "dxcc": "Russia",
      "cqz": 16,
      "ituz": 30,
      "app_lotw_rxqsl": null,
      "vucc_grids": "",
      "iota": "",
      "lotw": "N",
      "paper_qsl": "N",
      "created_at": "2025-01-15T14:30:00Z",
      "updated_at": "2025-01-15T14:30:00Z"
    }
  ]
}
```

**Параметры пагинации:**
- `page` - номер страницы (по умолчанию 1)
- `page_size` - количество записей на странице (по умолчанию 100)

---

### 4. Получение конкретного QSO

**GET** `/api/v1/qsos/{id}/`

Получает конкретную запись QSO по ID.

**Пример запроса:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/qsos/550e8400-e29b-41d4-a716-446655440000/" \
  -H "Authorization: Basic dGVzdHVzZXI6dGVzdHBhc3M="
```

---

### 5. Создание QSO

**POST** `/api/v1/qsos/`

Создает новую запись QSO.

**Пример запроса:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/qsos/" \
  -H "Authorization: Basic dGVzdHVzZXI6dGVzdHBhc3M=" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-01-15",
    "time": "14:30:00",
    "my_callsign": "UA0AAA",
    "callsign": "UA0BBB",
    "frequency": 14.070,
    "band": "20M",
    "mode": "FT8",
    "rst_sent": "599",
    "rst_rcvd": "599",
    "my_gridsquare": "KN88",
    "gridsquare": "KO85"
  }'
```

**Пример ответа:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "date": "2025-01-15",
  "time": "14:30:00",
  "my_callsign": "UA0AAA",
  "callsign": "UA0BBB",
  ...
  "created_at": "2025-01-15T14:30:00Z",
  "updated_at": "2025-01-15T14:30:00Z"
}
```

---

### 6. Обновление QSO

**PATCH** `/api/v1/qsos/{id}/`

Частично обновляет запись QSO.

**Пример запроса:**
```bash
curl -X PATCH "http://127.0.0.1:8000/api/v1/qsos/550e8400-e29b-41d4-a716-446655440000/" \
  -H "Authorization: Basic dGVzdHVzZXI6dGVzdHBhc3M=" \
  -H "Content-Type: application/json" \
  -d '{
    "rst_sent": "579",
    "rst_rcvd": "579"
  }'
```

---

### 7. Удаление QSO

**DELETE** `/api/v1/qsos/{id}/`

Удаляет запись QSO.

**Пример запроса:**
```bash
curl -X DELETE "http://127.0.0.1:8000/api/v1/qsos/550e8400-e29b-41d4-a716-446655440000/" \
  -H "Authorization: Basic dGVzdHVzZXI6dGVzdHBhc3M="
```

**Ответ:** `204 No Content`

---

### 8. Статистика QSO

**GET** `/api/v1/qsos/stats/`

Получает статистику QSO текущего пользователя.

**Пример запроса:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/qsos/stats/" \
  -H "Authorization: Basic dGVzdHVzZXI6dGVzdHBhc3M="
```

**Пример ответа:**
```json
{
  "total_qso": 150,
  "unique_callsigns": 75,
  "dxcc_count": 30,
  "band_statistics": {
    "20M": 50,
    "40M": 30,
    "80M": 20,
    "15M": 25,
    "10M": 25
  },
  "mode_statistics": {
    "FT8": 80,
    "SSB": 40,
    "CW": 30
  },
  "year_statistics": {
    "2025": 100,
    "2024": 50
  }
}
```

---

### 9. Поиск QSO по позывному

**GET** `/api/v1/qsos/search/?callsign={callsign}`

Ищет QSO по позывному корреспондента (частичное совпадение).

**Пример запроса:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/qsos/search/?callsign=UA" \
  -H "Authorization: Basic dGVzdHVzZXI6dGVzdHBhc3M="
```

---

### 10. Получение QSO по диапазону

**GET** `/api/v1/qsos/by_band/?band={band}`

Получает QSO по диапазону.

**Пример запроса:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/qsos/by_band/?band=20M" \
  -H "Authorization: Basic dGVzdHVzZXI6dGVzdHBhc3M="
```

---

## Коды ответов

- `200 OK` - Успешный запрос
- `201 Created` - Ресурс успешно создан
- `204 No Content` - Успешное удаление
- `400 Bad Request` - Неверные данные запроса
- `401 Unauthorized` - Требуется аутентификация
- `403 Forbidden` - Нет прав доступа
- `404 Not Found` - Ресурс не найден
- `500 Internal Server Error` - Ошибка сервера

---

## Примеры на Python

### Базовый запрос с аутентификацией

```python
import requests
import base64

BASE_URL = 'http://127.0.0.1:8000'
USERNAME = 'your_username'
PASSWORD = 'your_password'

# Создаем заголовок с Basic Authentication
credentials = f"{USERNAME}:{PASSWORD}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()
headers = {
    'Authorization': f'Basic {encoded_credentials}',
    'Content-Type': 'application/json'
}

# Получаем список QSO
response = requests.get(f'{BASE_URL}/api/v1/qsos/', headers=headers)

if response.status_code == 200:
    data = response.json()
    print(f"Всего QSO: {data['count']}")
    for qso in data['results']:
        print(f"{qso['date']} {qso['time']} - {qso['callsign']} ({qso['band']})")
else:
    print(f"Ошибка: {response.status_code}")
    print(response.json())
```

### Создание QSO

```python
qso_data = {
    "date": "2025-01-15",
    "time": "14:30:00",
    "my_callsign": "UA0AAA",
    "callsign": "UA0BBB",
    "frequency": 14.070,
    "band": "20M",
    "mode": "FT8",
    "rst_sent": "599",
    "rst_rcvd": "599",
}

response = requests.post(
    f'{BASE_URL}/api/v1/qsos/',
    headers=headers,
    json=qso_data
)

if response.status_code == 201:
    print("QSO создан успешно!")
    print(response.json())
else:
    print("Ошибка создания QSO:")
    print(response.json())
```

---

## Тестирование API

Для автоматического тестирования API используйте скрипт `test_rest_api.py`:

```bash
# Измените USERNAME и PASSWORD в скрипте
python test_rest_api.py
```

Скрипт выполнит все основные операции и покажет результаты.

---

## Безопасность

⚠️ **Важно:** Basic Authentication передает пароль в закодированном (но не зашифрованном) виде!

**Рекомендации:**
- Используйте только через **HTTPS** в production
- Для production рассмотрите переход на **Token Authentication** или **JWT**
- Ограничьте доступ к API по IP-адресам