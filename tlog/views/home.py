# Основные страницы и общие функции

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.utils import timezone
from datetime import timedelta
import json
import time
import os
from ..models import QSO, RadioProfile, ADIFUpload, check_user_blocked, ChatMessage


def home(request):
    """
    Главная страница с формой входа
    """
    # Если пользователь уже аутентифицирован, перенаправляем на dashboard или на next параметр
    if request.user.is_authenticated:
        next_url = request.GET.get('next', '/lotw/')
        return redirect(next_url)

    total_users = User.objects.count()
    total_qso = QSO.objects.count()

    # Обработка формы входа
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('rememberMe')

        if username and password:
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                is_blocked, reason = check_user_blocked(user)
                if is_blocked:
                    # Перенаправляем на страницу блокировки
                    return redirect('blocked_page', reason=reason or 'Доступ заблокирован администратором')
                else:
                    login(request, user)
                    
                    # Определяем страницу для перенаправления после входа
                    next_url = request.POST.get('next') or request.GET.get('next') or '/lotw/'

                    # Обработка "Запомнить меня"
                    if remember_me:
                        request.session.set_expiry(30 * 24 * 60 * 60)  # 30 дней
                    else:
                        request.session.set_expiry(0)  # До закрытия браузера
                    
                    messages.success(request, f'Добро пожаловать, {user.username}!')
                    return redirect(next_url)
            else:
                messages.error(request, 'Неверный логин или пароль.')
        else:
            messages.error(request, 'Пожалуйста, заполните все поля.')

    return render(request, 'index.html', {
        'total_users': total_users,
        'total_qso': total_qso,
    })


def get_callsigns_list(request):
    """
    Получение списка уникальных позывных пользователей для автодополнения
    """
    query = request.GET.get('q', '').upper()
    if len(query) < 1:
        return JsonResponse({'callsigns': []})

    callsigns_set = set()

    # 1. Ищем в поле callsign модели RadioProfile
    profiles_with_callsign = RadioProfile.objects.filter(
        callsign__icontains=query
    ).exclude(callsign='').values_list('callsign', flat=True).distinct()
    callsigns_set.update([c.upper() for c in profiles_with_callsign])

    # 2. Ищем в поле my_callsigns (JSON) модели RadioProfile
    profiles = RadioProfile.objects.filter(
        my_callsigns__isnull=False
    ).exclude(
        my_callsigns=[]
    ).exclude(
        my_callsigns=''
    )

    import json
    for profile in profiles:
        try:
            my_callsigns = json.loads(profile.my_callsigns) if isinstance(profile.my_callsigns, str) else profile.my_callsigns
            if isinstance(my_callsigns, list):
                for item in my_callsigns:
                    if isinstance(item, dict) and 'name' in item:
                        name = item['name'].upper()
                        if query in name:
                            callsigns_set.add(name)
                    elif isinstance(item, str):
                        name = item.upper()
                        if query in name:
                            callsigns_set.add(name)
        except (json.JSONDecodeError, TypeError):
            pass

    # 3. Также ищем в QSO (my_callsign)
    qso_callsigns = QSO.objects.filter(
        my_callsign__icontains=query
    ).values_list('my_callsign', flat=True).distinct()
    callsigns_set.update([c.upper() for c in qso_callsigns])

    # Ограничиваем до 10 результатов и сортируем
    callsigns_list = sorted(list(callsigns_set))[:10]

    return JsonResponse({'callsigns': callsigns_list})


def debug_callsigns(request):
    """
    Отладочная страница для проверки загрузки и сохранения позывных
    """
    if not request.user.is_authenticated:
        return redirect('login_page')

    # Получаем или создаем профиль
    try:
        profile = RadioProfile.objects.get(user=request.user)
    except RadioProfile.DoesNotExist:
        profile = RadioProfile.objects.create(user=request.user)

    if request.method == 'POST':
        try:
            # Обрабатываем my_callsigns из JSON
            my_callsigns_json = request.POST.get('my_callsigns_json', '[]')
            try:
                new_my_callsigns = json.loads(my_callsigns_json)
            except json.JSONDecodeError:
                new_my_callsigns = []

            # Сохраняем данные
            profile.my_callsigns = new_my_callsigns
            profile.save()

            messages.success(request, f'Данные сохранены! Получено: {new_my_callsigns}')
        except Exception as e:
            messages.error(request, f'Ошибка при сохранении: {str(e)}')

    return render(request, 'debug_register.html', {
        'profile': profile,
    })


def test_callsigns_simple(request):
    """
    Простая тестовая страница для проверки сохранения позывных
    """
    if not request.user.is_authenticated:
        return redirect('login_page')

    # Получаем или создаем профиль
    try:
        profile = RadioProfile.objects.get(user=request.user)
    except RadioProfile.DoesNotExist:
        profile = RadioProfile.objects.create(user=request.user)

    if request.method == 'POST':
        try:
            # Обрабатываем my_callsigns из JSON
            my_callsigns_json = request.POST.get('my_callsigns_json', '[]')
            try:
                new_my_callsigns = json.loads(my_callsigns_json)
            except json.JSONDecodeError:
                new_my_callsigns = []

            # Сохраняем данные
            profile.my_callsigns = new_my_callsigns
            profile.save()

            messages.success(request, f'Данные сохранены! Получено: {new_my_callsigns}')
        except Exception as e:
            messages.error(request, f'Ошибка при сохранении: {str(e)}')

    return render(request, 'test_callsigns_simple.html', {
        'profile': profile,
    })


def custom_404_view(request, exception):
    """
    Обработчик ошибки 404 - страница не найдена
    """
    return render(request, '404.html', {
        'request_path': request.path,
    }, status=404)