#!/bin/bash

echo "🛑 Остановка тестовых серверов..."

pkill -f "python manage.py runserver"
pkill -f "python3 -m http.server 8080"

sleep 1

echo "✅ Серверы остановлены"

# Проверка
if pgrep -f "python manage.py runserver" > /dev/null; then
    echo "⚠️  Django сервер всё ещё работает"
else
    echo "✅ Django сервер остановлен"
fi

if pgrep -f "python3 -m http.server 8080" > /dev/null; then
    echo "⚠️  HTTP сервер всё ещё работает"
else
    echo "✅ HTTP сервер остановлен"
fi
