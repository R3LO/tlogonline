# Добавляем кастомный фильтр для JSON в Django
import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def json_filter(value):
    """Конвертирует Python объект в JSON строку для использования в JavaScript"""
    if value is None:
        return '[]'
    json_str = json.dumps(value, ensure_ascii=False)
    # Возвращаем как safe строку, чтобы не экранировались кавычки
    return mark_safe(json_str)