@echo off
REM Скрипт для запуска TLog REST API Client на Windows

REM Переходим в директорию скрипта
cd /d "%~dp0"

echo.
echo === TLog REST API Client ===
echo.

REM Проверка наличия venv
if not exist "venv" (
    echo Создание виртуального окружения...
    python -m venv venv
    if errorlevel 1 (
        echo Ошибка создания виртуального окружения
        pause
        exit /b 1
    )
)

REM Активация venv
call venv\Scripts\activate.bat

REM Проверка зависимостей
echo Проверка зависимостей...
pip show PySide6 >nul 2>&1
if errorlevel 1 (
    echo Установка зависимостей...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Ошибка установки зависимостей
        pause
        exit /b 1
    )
)

REM Запуск приложения из родительской директории (чтобы работал импорт rest_api_client.main)
cd ..
echo.
echo Запуск приложения...
echo.
python -m rest_api_client.main

pause
