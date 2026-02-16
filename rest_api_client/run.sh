#!/bin/bash
# Скрипт для запуска TLog REST API Client на Linux/Mac

# Переходим в директорию скрипта
cd "$(dirname "$0")"

echo ""
echo "=== TLog REST API Client ==="
echo ""

# Проверка наличия venv
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Ошибка создания виртуального окружения"
        exit 1
    fi
fi

# Активация venv
source venv/bin/activate

# Проверка зависимостей
echo "Проверка зависимостей..."
pip show PySide6 > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Установка зависимостей..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Ошибка установки зависимостей"
        exit 1
    fi
fi

# Запуск приложения из родительской директории (чтобы работал импорт rest_api_client.main)
cd ..
echo ""
echo "Запуск приложения..."
echo ""
python -m rest_api_client.main
