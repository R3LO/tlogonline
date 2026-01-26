import re

with open('tlog/templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Добавляем dashboard.css после Bootstrap
pattern = r'(<link href="https://cdn\.jsdelivr\.net/npm/bootstrap@5\.3\.0/dist/css/bootstrap\.min\.css" rel="stylesheet">)\n\n(</head>)'
replacement = r'''\1
    <link href="{% static 'css/dashboard.css' %}" rel="stylesheet">

\2'''

new_content = re.sub(pattern, replacement, content)

with open('tlog/templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('CSS added')