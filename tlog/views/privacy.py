"""
Представления для страницы приватности
"""
from django.shortcuts import render


def privacy(request):
    """
    Страница политики конфиденциальности
    """
    return render(request, 'privacy.html')
