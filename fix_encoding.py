import shutil

# Копируем файл из репозитория
shutil.copy('tlog/templates/dashboard_new.html', 'tlog/templates/dashboard.html')

# Проверяем кодировку
with open('tlog/templates/dashboard.html', 'rb') as f:
    content = f.read()
    print(f"First bytes: {content[:10].hex()}")

# Читаем с utf-16-le (с BOM fffe)
with open('tlog/templates/dashboard.html', 'r', encoding='utf-16-le') as f:
    text = f.read()

# Перезаписываем с чистой UTF-8
with open('tlog/templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("File fixed")