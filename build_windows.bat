@echo off
REM Скрипт для сборки Windows exe файла
REM Запустите этот файл на Windows машине с установленным Python

echo === TLog REST API Client - Build Script ===
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Ошибка: Python не установлен или не найден в PATH
    echo Пожалуйста, установите Python с https://www.python.org/
    pause
    exit /b 1
)

echo Установка зависимостей...
pip install -r requirements_client.txt
if %errorlevel% neq 0 (
    echo Ошибка при установке зависимостей
    pause
    exit /b 1
)

echo.
echo Установка PyInstaller...
pip install pyinstaller
if %errorlevel% neq 0 (
    echo Ошибка при установке PyInstaller
    pause
    exit /b 1
)

echo.
echo Сборка exe файла...
pyinstaller --onefile --windowed --name "TLogSearch" --icon=icon.ico rest_api_client/main.py
if %errorlevel% neq 0 (
    echo Ошибка при сборке exe файла
    pause
    exit /b 1
)

echo.
echo === Сборка завершена ===
echo exe файл находится в папке: dist\TLogSearch.exe
echo.
pause
