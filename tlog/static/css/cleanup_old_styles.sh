#!/bin/bash

# Скрипт для очистки старых стилей
# Дата создания: $(date)

echo "=== Создание резервной копии старых стилей ==="

# Создаем папку для резервных копий
mkdir -p old_styles_backup

# Копируем старые файлы в резервную папку
cp achievements.css old_styles_backup/
cp common.css old_styles_backup/
cp common_backup.css old_styles_backup/
cp cosmos_diploma.css old_styles_backup/
cp dashboard.css old_styles_backup/
cp index.css old_styles_backup/
cp logbook.css old_styles_backup/
cp logbook_main.css old_styles_backup/
cp login.css old_styles_backup/
cp lotw.css old_styles_backup/
cp privacy.css old_styles_backup/
cp profile_edit.css old_styles_backup/
cp register.css old_styles_backup/

echo "Резервные копии созданы в папке old_styles_backup/"

echo "=== Удаление старых файлов стилей ==="

# Удаляем старые файлы
rm achievements.css
rm common.css
rm common_backup.css
rm cosmos_diploma.css
rm dashboard.css
rm index.css
rm logbook.css
rm logbook_main.css
rm login.css
rm lotw.css
rm privacy.css
rm profile_edit.css
rm register.css

echo "Старые файлы стилей удалены"

echo "=== Очистка завершена ==="
echo "Теперь используются только новые модульные стили:"
echo "- main.css (главный файл)"
echo "- variables.css (переменные)"
echo "- base.css (базовые стили)"
echo "- components.css (компоненты)"
echo "- layout.css (макеты)"
echo "- pages.css (страничные стили)"
echo "- utilities.css (утилиты)"
echo "- responsive.css (адаптивность)"