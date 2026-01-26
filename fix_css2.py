with open('tlog/templates/dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

result = []
skip = False
for i, line in enumerate(lines):
    if 'bootstrap.min.css' in line and not skip:
        result.append(line)
        # Добавляем следующую строку - пустую
        result.append('    <link href="{% static \'css/dashboard.css\' %}" rel="stylesheet">\n')
        skip = True
    elif line.strip() == '</head>' and i > 0 and lines[i-1].strip() == '':
        # Если предыдущая строка пустая и это </head>, пропускаем
        continue
    else:
        result.append(line)

with open('tlog/templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.writelines(result)

print('Done')