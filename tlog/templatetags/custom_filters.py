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