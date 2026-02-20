#!/bin/bash

# Скрипт для запуска тестовых серверов

echo "🚀 Запуск тестовых серверов..."

# Останавливаем предыдущие процессы
echo "🛑 Остановка предыдущих процессов..."
pkill -f "python manage.py runserver" 2>/dev/null
pkill -f "python3 -m http.server 8080" 2>/dev/null

# Ждем завершения
sleep 1

# Запускаем Django сервер
echo "📡 Запуск Django сервера на порту 8000..."
source venv/bin/activate
python manage.py runserver 127.0.0.1:8000 > /tmp/django_server.log 2>&1 &
DJANGO_PID=$!
echo "   Django PID: $DJANGO_PID"

# Запускаем HTTP сервер для HTML файлов
echo "🌐 Запуск HTTP сервера на порту 8080..."
python3 -m http.server 8080 > /tmp/http_server.log 2>&1 &
HTTP_PID=$!
echo "   HTTP Server PID: $HTTP_PID"

# Ждем запуска серверов
echo "⏳ Ожидание запуска серверов..."
sleep 3

# Проверяем, что серверы запущены
echo ""
echo "🔍 Проверка серверов..."

# Проверка Django
if curl -s http://127.0.0.1:8000/api/v1/public/qso-search/?callsign=TEST > /dev/null; then
    echo "✅ Django сервер запущен: http://127.0.0.1:8000"
else
    echo "❌ Ошибка запуска Django сервера"
    echo "Лог Django сервера:"
    tail -20 /tmp/django_server.log
    exit 1
fi

# Проверка HTTP сервера
if curl -s -I http://127.0.0.1:8080/test_qrz_form.html > /dev/null; then
    echo "✅ HTTP сервер запущен: http://127.0.0.1:8080"
else
    echo "❌ Ошибка запуска HTTP сервера"
    exit 1
fi

echo ""
echo "📝 Открытие тестовой страницы в браузере..."

# Определяем команду для открытия браузера
if command -v xdg-open > /dev/null; then
    xdg-open http://127.0.0.1:8080/test_qrz_form.html
elif command -v open > /dev/null; then
    open http://127.0.0.1:8080/test_qrz_form.html
elif command -v firefox > /dev/null; then
    firefox http://127.0.0.1:8080/test_qrz_form.html &
elif command -v google-chrome > /dev/null; then
    google-chrome http://127.0.0.1:8080/test_qrz_form.html &
else
    echo "⚠️  Не удалось автоматически открыть браузер"
    echo "📌 Откройте вручную: http://127.0.0.1:8080/test_qrz_form.html"
fi

echo ""
echo "✅ Серверы запущены!"
echo ""
echo "📌 Тестовая страница: http://127.0.0.1:8080/test_qrz_form.html"
echo "📌 Django API: http://127.0.0.1:8000/api/v1/public/qso-search/"
echo ""
echo "🛑 Для остановки серверов нажмите Ctrl+C или запустите:"
echo "   pkill -f 'python manage.py runserver'"
echo "   pkill -f 'python3 -m http.server 8080'"
echo ""
echo "⏳ Серверы работают... (Ctrl+C для остановки)"

# Ожидание Ctrl+C
trap "echo ''; echo '🛑 Остановка серверов...'; kill $DJANGO_PID $HTTP_PID 2>/dev/null; exit 0" INT TERM

# Держим скрипт запущенным
while true; do
    sleep 1
done
