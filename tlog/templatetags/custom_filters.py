from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Доступ к элементу словаря по ключу"""
    if dictionary is None:
        return None
    return dictionary.get(key, None)


@register.filter
def index(List, i):
    """Доступ к элементу списка по индексу"""
    try:
        return List[int(i)]
    except (IndexError, TypeError, ValueError):
        return None


@register.filter
def startswith(text, prefix):
    """
    Check if text starts with prefix
    Usage: {% if text|startswith:"SAT:" %}
    """
    if text is None:
        return False
    return str(text).startswith(prefix)


@register.simple_tag
def paginate_numbers(current_page, total_pages, range_size=3):
    """
    Генерирует список номеров страниц для отображения.
    Показывает первые, последние и несколько вокруг текущей.
    """
    pages = []

    if total_pages <= 7:
        # Если мало страниц, показываем все
        pages = list(range(1, total_pages + 1))
    else:
        # Всегда показываем первую страницу
        pages.append(1)

        # Показываем текущую страницу и окружающие
        start = max(2, current_page - range_size)
        end = min(total_pages, current_page + range_size)

        # Добавляем многоточие если есть разрыв между началом и началом диапазона
        if start > 2:
            pages.append('...')

        # Добавляем страницы вокруг текущей
        for p in range(start, end + 1):
            if p not in pages:
                pages.append(p)

        # Добавляем многоточие если есть разрыв между концом диапазона и последней страницей
        if end < total_pages - 1:
            pages.append('...')

        # Всегда показываем последнюю страницу
        if total_pages not in pages:
            pages.append(total_pages)

    return pages
