# REST API Documentation

## Обзор

API предоставляет доступ к данным радиолюбительского логбука через REST интерфейс с использованием Basic Authentication.

## Базовый URL

```
http://127.0.0.1:8000/api/v1/
```

## Аутентификация

API использует **Basic Authentication**. Для каждого запроса необходимо отправлять заголовок `Authorization`:

```
Authorization: Basic base64(username:password)
```

### Пример на Python

```python
import base64
import requests

username = "your_username"
password = "your_password"
credentials = base64.b64encode(f"{username}:{password}".encode()).decode()

headers = {
    'Authorization': f'Basic {credentials}',
    'Content-Type': 'application/json'
}

response = requests.get('http://127.0.0.1:8000/api/v1/user-info/', headers=headers)
```

### Пример на cURL

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/user-info/" \
  -H "Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ="
```

---

## Endpoints

### 1. Информация о пользователе

Получить базовую информацию о текущем пользователе.

**Endpoint:** `GET /api/v1/user-info/`

**Ответ:**
```json
{
  "id": 1,
  "username": "ua0aaa",
  "email": "user@example.com",
  "first_name": "Иван",
  "last_name": "Иванов",
  "date_joined": "2024-01-01T00:00:00Z"
}
```

---

### 2. Профиль пользователя

Получить профиль радиолюбителя.

**Endpoint:** `GET /api/v1/profile/`

**Ответ:**
```json
{
  "username": "ua0aaa",
  "email": "user@example.com",
  "first_name": "Иван",
  "last_name": "Иванов",
  "callsign": "UA0AAA",
  "qth": "Москва",
  "my_gridsquare": "KN88",
  "lotw_user": "lotw_username",
  "lotw_chk_pass": true,
  "lotw_lastsync": "2024-01-15T10:30:00Z",
  "my_callsigns": ["UA0AAA", "UA0AAA/P"],
  "is_blocked": false,
  "blocked_reason": "",
  "blocked_at": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Обновление профиля:** `PATCH /api/v1/profile/`

```json
{
  "qth": "Новгород",
  "my_gridsquare": "KO85"
}
```

---

### 3. Список QSO

Получить список всех QSO текущего пользователя.

**Endpoint:** `GET /api/v1/qsos/`

**Параметры запроса:**
- `page` - номер страницы (по умолчанию 1)
- `page_size` - количество записей на странице (по умолчанию 100)

**Ответ:**
```json
{
  "count": 150,
  "next": "http://127.0.0.1:8000/api/v1/qsos/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid-here",
      "date": "2024-01-15",
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
      "created_at": "2024-01-15T14:30:00Z",
      "updated_at": "2024-01-15T14:30:00Z"
    }
  ]
}
```

---

### 4. Создание QSO

Создать новую запись QSO.

**Endpoint:** `POST /api/v1/qsos/`

**Тело запроса:**
```json
{
  "date": "2024-01-15",
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
}
```

**Ответ:** `201 Created` с созданным объектом QSO.

---

### 5. Получение конкретного QSO

Получить информацию о конкретном QSO по ID.

**Endpoint:** `GET /api/v1/qsos/{id}/`

**Пример:** `GET /api/v1/qsos/uuid-here/`

**Ответ:** Объект QSO (как в списке QSO).

---

### 6. Обновление QSO

Обновить существующий QSO.

**Endpoint:** `PATCH /api/v1/qsos/{id}/` или `PUT /api/v1/qsos/{id}/`

**Тело запроса (только обновляемые поля):**
```json
{
  "rst_sent": "579",
  "rst_rcvd": "579"
}
```

**Ответ:** `200 OK` с обновленным объектом QSO.

---

### 7. Удаление QSO

Удалить существующий QSO.

**Endpoint:** `DELETE /api/v1/qsos/{id}/`

**Пример:** `DELETE /api/v1/qsos/uuid-here/`

**Ответ:** `204 No Content`

---

### 8. Статистика QSO

Получить статистику QSO текущего пользователя.

**Endpoint:** `GET /api/v1/qsos/stats/`

**Ответ:**
```json
{
  "total_qso": 150,
  "unique_callsigns": 95,
  "dxcc_count": 45,
  "band_statistics": {
    "20M": 50,
    "40M": 30,
    "15M": 25,
    "10M": 20,
    "2M": 15,
    "70CM": 10
  },
  "mode_statistics": {
    "FT8": 80,
    "SSB": 40,
    "CW": 20,
    "RTTY": 10
  },
  "year_statistics": {
    "2024": 100,
    "2023": 50
  }
}
```

---

### 9. Поиск QSO по позывному

Поиск QSO по позывному корреспондента.

**Endpoint:** `GET /api/v1/qsos/search/?callsign={callsign}`

**Параметры:**
- `callsign` - позывной для поиска (частичное совпадение)

**Пример:** `GET /api/v1/qsos/search/?callsign=UA0`

**Ответ:** Массив объектов QSO.

---

### 10. Получение QSO по диапазону

Получить QSO по определённому диапазону.

**Endpoint:** `GET /api/v1/qsos/by_band/?band={band}`

**Параметры:**
- `band` - диапазон (например, 20M, 40M, 2M)

**Пример:** `GET /api/v1/qsos/by_band/?band=20M`

**Ответ:** Массив объектов QSO.

---

## Коды ответов

| Код | Описание |
|-----|----------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request - ошибка валидации данных |
| 401 | Unauthorized - неверные учетные данные |
| 403 | Forbidden - нет доступа |
| 404 | Not Found - ресурс не найден |
| 500 | Internal Server Error - ошибка сервера |

---

## Установка зависимостей

```bash
pip install djangorestframework==3.15.2
```

---

## Запуск тестов

Создайте файл `test_rest_api.py` (см. пример в репозитории) и запустите:

```bash
python test_rest_api.py
```

Не забудьте заменить `USERNAME` и `PASSWORD` на ваши учетные данные.

---

## Безопасность

⚠️ **Важно:** Basic Authentication передает логин и пароль в заголовке каждого запроса. Для production-среды рекомендуется использовать:

1. **HTTPS** для шифрования трафика
2. **Token Authentication** или **JWT** вместо Basic Authentication
3. Ограничение количества запросов (Rate Limiting)

---

## Примеры использования

### Python

```python
import requests
import base64

# Настройка
BASE_URL = 'http://127.0.0.1:8000/api/v1/'
USERNAME = 'your_username'
PASSWORD = 'your_password'

# Создание заголовков
credentials = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
headers = {
    'Authorization': f'Basic {credentials}',
    'Content-Type': 'application/json'
}

# Получение статистики
response = requests.get(f'{BASE_URL}qsos/stats/', headers=headers)
stats = response.json()
print(f"Всего QSO: {stats['total_qso']}")

# Создание QSO
new_qso = {
    "date": "2024-01-15",
    "time": "14:30:00",
    "my_callsign": "UA0AAA",
    "callsign": "UA0BBB",
    "band": "20M",
    "mode": "FT8"
}
response = requests.post(f'{BASE_URL}qsos/', headers=headers, json=new_qso)
print(f"Создано QSO: {response.json()['id']}")
```

### JavaScript (fetch)

```javascript
const BASE_URL = 'http://127.0.0.1:8000/api/v1/';
const USERNAME = 'your_username';
const PASSWORD = 'your_password';

// Создание заголовков
const headers = new Headers();
headers.append('Authorization', 'Basic ' + btoa(USERNAME + ':' + PASSWORD));
headers.append('Content-Type', 'application/json');

// Получение статистики
fetch(BASE_URL + 'qsos/stats/', { headers })
  .then(response => response.json())
  .then(stats => {
    console.log('Всего QSO:', stats.total_qso);
  });

// Создание QSO
const newQSO = {
  date: '2024-01-15',
  time: '14:30:00',
  my_callsign: 'UA0AAA',
  callsign: 'UA0BBB',
  band: '20M',
  mode: 'FT8'
};

fetch(BASE_URL + 'qsos/', {
  method: 'POST',
  headers,
  body: JSON.stringify(newQSO)
})
  .then(response => response.json())
  .then(qso => {
    console.log('Создано QSO:', qso.id);
  });
```
