# Форма поиска QSO для QRZ.com

Этот файл содержит код формы поиска, которую можно встроить на страницу QRZ.com.

## Инструкция по установке

1. **Скопируйте код ниже** и вставьте его в поле "Bio" или любое другое поле, поддерживающее HTML, на вашем профиле QRZ.com

2. **Замените `YOUR_TLOGONLINE_URL`** на ваш реальный URL сервера tlogonline.com:
   - Для production: `https://tlogonline.com`
   - Для тестирования: `http://your-server-ip` или `http://localhost:8000`

3. **Сохраните изменения** на QRZ.com

## Код формы для вставки на QRZ.com

```html
<!-- TlogOnline QSO Search Form -->
<div id="tlog-search-container" style="font-family: Arial, sans-serif; max-width: 800px; margin: 20px auto;">
    <style>
        #tlog-search-container {
            background: #f5f5f5;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
        }
        #tlog-search-form {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        #tlog-callsign-input {
            flex: 1;
            min-width: 200px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 14px;
        }
        #tlog-search-btn {
            padding: 10px 20px;
            background: #0066cc;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
        }
        #tlog-search-btn:hover {
            background: #0052a3;
        }
        #tlog-search-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        #tlog-result {
            margin-top: 20px;
        }
        #tlog-result-table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 4px;
            overflow: hidden;
        }
        #tlog-result-table th,
        #tlog-result-table td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        #tlog-result-table th {
            background: #0066cc;
            color: white;
            font-weight: bold;
        }
        #tlog-result-table tr:hover {
            background: #f9f9f9;
        }
        .tlog-mode-count {
            background: #e6f3ff;
            padding: 2px 8px;
            border-radius: 12px;
            font-weight: bold;
            color: #0066cc;
        }
        #tlog-loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        #tlog-error {
            background: #ffe6e6;
            color: #cc0000;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
        }
        #tlog-not-found {
            background: #fff3cd;
            color: #856404;
            padding: 15px;
            border-radius: 4px;
            text-align: center;
            margin-top: 10px;
            font-weight: bold;
        }
        .tlog-title {
            color: #0066cc;
            margin-bottom: 15px;
            font-size: 18px;
            font-weight: bold;
            text-align: center;
        }
    </style>

    <div class="tlog-title">📻 Поиск QSO в логе</div>

    <form id="tlog-search-form">
        <input
            type="text"
            id="tlog-callsign-input"
            placeholder="Введите позывной (например: UA0AAA)"
            maxlength="20"
        />
        <button type="submit" id="tlog-search-btn">Найти</button>
    </form>

    <div id="tlog-result"></div>
</div>

<script>
(function() {
    // ==================== КОНФИГУРАЦИЯ ====================
    // ЗАМЕНИТЕ НА ВАШ РЕАЛЬНЫЙ URL СЕРВЕРА
    const API_BASE_URL = 'https://tlogonline.com';  // Измените на ваш URL
    // =====================================================

    const form = document.getElementById('tlog-search-form');
    const input = document.getElementById('tlog-callsign-input');
    const button = document.getElementById('tlog-search-btn');
    const resultDiv = document.getElementById('tlog-result');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const callsign = input.value.trim().toUpperCase();

        if (!callsign) {
            showError('Пожалуйста, введите позывной');
            return;
        }

        // Проверка формата позывного (базовая)
        const callsignRegex = /^[A-Z0-9\/]+$/;
        if (!callsignRegex.test(callsign)) {
            showError('Неверный формат позывного. Используйте только буквы, цифры и символ /');
            return;
        }

        showLoading();
        button.disabled = true;

        try {
            const response = await fetch(
                `${API_BASE_URL}/api/v1/public/qso-search/?callsign=${encodeURIComponent(callsign)}`,
                {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                }
            );

            if (!response.ok) {
                throw new Error(`Ошибка сервера: ${response.status}`);
            }

            const data = await response.json();
            displayResults(data);

        } catch (error) {
            console.error('Ошибка поиска:', error);
            showError(`Ошибка при поиске: ${error.message}. Проверьте соединение с сервером.`);
        } finally {
            button.disabled = false;
        }
    });

    function showLoading() {
        resultDiv.innerHTML = '<div id="tlog-loading">⏳ Поиск...</div>';
    }

    function showError(message) {
        resultDiv.innerHTML = `<div id="tlog-error">❌ ${message}</div>`;
    }

    function displayResults(data) {
        if (!data.found) {
            resultDiv.innerHTML = `
                <div id="tlog-not-found">
                    📭 Для позывного <strong>${data.callsign || ''}</strong> ничего не найдено
                </div>
            `;
            return;
        }

        if (!data.results || data.results.length === 0) {
            resultDiv.innerHTML = `
                <div id="tlog-not-found">
                    📭 Для позывного <strong>${data.callsign}</strong> ничего не найдено
                </div>
            `;
            return;
        }

        // Собираем все уникальные модуляции
        const allModes = new Set();
        data.results.forEach(result => {
            Object.keys(result.modes).forEach(mode => allModes.add(mode));
        });
        const sortedModes = Array.from(allModes).sort();

        // Создаем таблицу
        let html = `
            <table id="tlog-result-table">
                <thead>
                    <tr>
                        <th>Мой позывной</th>
                        ${sortedModes.map(mode => `<th>${mode}</th>`).join('')}
                        <th>Всего</th>
                    </tr>
                </thead>
                <tbody>
        `;

        data.results.forEach(result => {
            const totalQSO = Object.values(result.modes).reduce((a, b) => a + b, 0);
            html += `
                <tr>
                    <td><strong>${result.my_callsign}</strong></td>
                    ${sortedModes.map(mode => {
                        const count = result.modes[mode] || 0;
                        return count > 0
                            ? `<td><span class="tlog-mode-count">${count}</span></td>`
                            : '<td>-</td>';
                    }).join('')}
                    <td><strong>${totalQSO}</strong></td>
                </tr>
            `;
        });

        html += `
                </tbody>
            </table>
            <p style="margin-top: 10px; font-size: 12px; color: #666; text-align: center;">
                ✅ Найдено QSO для позывного <strong>${data.callsign}</strong>
            </p>
        `;

        resultDiv.innerHTML = html;
    }

    // Автофокус на поле ввода при загрузке
    window.addEventListener('load', function() {
        input.focus();
    });

    // Обработка Enter
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            form.dispatchEvent(new Event('submit'));
        }
    });
})();
</script>
<!-- End TlogOnline QSO Search Form -->
```

## Тестирование формы

1. После вставки кода на QRZ.com, откройте ваш профиль
2. Введите любой позывной в поле поиска
3. Нажмите кнопку "Найти"
4. Вы должны увидеть таблицу с результатами или сообщение "Ничего не найдено"

## Пример работы API

**Запрос:**
```
GET https://tlogonline.com/api/v1/public/qso-search/?callsign=UA0AAA
```

**Ответ (если найдено):**
```json
{
    "found": true,
    "callsign": "UA0AAA",
    "results": [
        {
            "my_callsign": "UA0AAA",
            "modes": {
                "SSB": 5,
                "CW": 3,
                "FT8": 10
            }
        },
        {
            "my_callsign": "UA0AAA/P",
            "modes": {
                "SSB": 2
            }
        }
    ]
}
```

**Ответ (если не найдено):**
```json
{
    "found": false,
    "callsign": "UA0XXX",
    "message": "Ничего не найдено"
}
```

## Особенности

- ✅ Не требует аутентификации (публичный API)
- ✅ Работает на сторонних сайтах (CORS настроен)
- ✅ Отображает результаты в виде таблицы
- ✅ Строки = my_callsign (ваши позывные)
- ✅ Колонки = виды модуляции
- ✅ Показывает количество QSO для каждой комбинации
- ✅ Адаптивный дизайн для мобильных устройств
- ✅ Валидация ввода позывного
- ✅ Обработка ошибок

## Установка зависимостей

Перед использованием убедитесь, что установлены все зависимости:

```bash
pip install django-cors-headers==4.6.0
```

## Настройка CORS (уже выполнено)

В файле `myproject/settings.py` добавлены следующие настройки:

```python
INSTALLED_APPS = [
    ...
    'corsheaders',
    ...
]

MIDDLEWARE = [
    ...
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    'https://qrz.com',
    'https://www.qrz.com',
    ...
]
```

## Перезапуск сервера

После внесения изменений перезапустите сервер:

```bash
# Для development
python manage.py runserver

# Для production (с использованием gunicorn)
gunicorn myproject.wsgi:application
```

## Безопасность

- API использует только GET запросы
- Нет возможности изменения данных через этот API
- Поиск только по полному совпадению callsign (без частичных совпадений)
- CORS ограничен только разрешенными доменами
