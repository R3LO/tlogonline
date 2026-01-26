with open('tlog/templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Извлекаем чат
import re
chat_match = re.search(r'<!-- Локальный чат -->\s*<div class="card chat-card mt-3">.*?</div>\s*</div>', content, re.DOTALL)
if chat_match:
    chat_html = chat_match.group(0)
    print(f'Found chat: {len(chat_html)} chars')

    # Удаляем чат из текущего места
    content = content.replace(chat_html, '')

    # Добавляем чат в сайдбар перед </div> закрывающим col-lg-4
    # Находим место для вставки - перед закрывающим </div> боковой панели
    sidebar_pattern = r'(<!-- Загруженные ADIF файлы -->.*?</div>\s*</div>\s*</div>\s*</div>\s*</div>)'
    sidebar_match = re.search(sidebar_pattern, content, re.DOTALL)
    if sidebar_match:
        new_sidebar = sidebar_match.group(1) + '\n\n' + chat_html.replace('mt-3', 'mb-3')
        content = content.replace(sidebar_match.group(1), new_sidebar)
        print('Chat moved to sidebar')
    else:
        print('Sidebar not found')
else:
    print('Chat not found')

with open('tlog/templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')