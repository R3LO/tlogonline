# Функции LoTW (Logbook of the World)

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
import requests
from ..models import RadioProfile, QSO, check_user_blocked


@login_required
def lotw_page(request):
    """
    Страница LoTW (Logbook of the World) - доступна только аутентифицированным пользователям
    """
    # Проверяем, не заблокирован ли пользователь
    is_blocked, reason = check_user_blocked(request.user)
    if is_blocked:
        return render(request, 'blocked.html', {'reason': reason})

    # Получаем данные пользователя для отображения статистики
    context = {}
    
    # Общая статистика QSO
    total_qso_count = QSO.objects.filter(user=request.user).count()
    context['total_qso_count'] = total_qso_count
    
    # QSO с подтверждением LoTW (только lotw = 'Y')
    lotw_confirmed_qso = QSO.objects.filter(user=request.user, lotw='Y')
    lotw_confirmed_count = lotw_confirmed_qso.count()
    context['lotw_confirmed_count'] = lotw_confirmed_count
    
    # Последние 10 QSO с подтверждением LoTW, отсортированные по дате подтверждения LoTW
    # Фильтруем только записи с заполненной датой app_lotw_rxqsl
    recent_lotw_qso = lotw_confirmed_qso.filter(app_lotw_rxqsl__isnull=False).order_by('-app_lotw_rxqsl', '-date', '-time')[:10]
    context['recent_lotw_qso'] = recent_lotw_qso
    
    # Уникальные DXCC entities
    dxcc_entities = lotw_confirmed_qso.exclude(dxcc__isnull=True).exclude(dxcc='').values('dxcc').distinct().count()
    context['dxcc_entities'] = dxcc_entities
    
    # Award credits (упрощенный расчет на основе подтвержденных QSO)
    # Можно расширить логику подсчета различных наград
    award_credits = lotw_confirmed_count  # Базовая логика - каждое подтверждение = 1 кредит
    context['award_credits'] = award_credits
    
    # Получаем профиль пользователя
    try:
        profile = RadioProfile.objects.get(user=request.user)
        context['profile'] = profile
    except RadioProfile.DoesNotExist:
        # Создаем пустой профиль если его нет
        context['profile'] = RadioProfile(user=request.user)

    return render(request, 'lotw.html', context)


@login_required
def verify_lotw_credentials(request):
    """
    Проверка логина и пароля LoTW
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    try:
        # Получаем логин и пароль из POST данных
        data = json.loads(request.body)
        login = data.get('login', '').strip()
        password = data.get('password', '').strip()

        if not login or not password:
            return JsonResponse({'error': 'Логин и пароль обязательны'}, status=400)

        # Функция проверки
        def check_lotw_pass(login, password):
            params = {
                'login': login,
                'password': password,
            }
            response = requests.get(
                "https://lotw.arrl.org/lotwuser/lotwreport.adi",
                params=params,
                timeout=15
            )
            if response.text.strip().startswith('ARRL Logbook of the World Status Report'):
                return True
            elif '<HTML>' in response.text.upper() or '<!DOCTYPE HTML' in response.text.upper():
                return False
            return False

        # Выполняем проверку
        is_valid = check_lotw_pass(login, password)

        # Обновляем профиль пользователя
        try:
            profile = RadioProfile.objects.get(user=request.user)
            profile.lotw_chk_pass = is_valid
            if is_valid:
                profile.lotw_user = login
                profile.lotw_password = password
            profile.save()
        except RadioProfile.DoesNotExist:
            pass

        return JsonResponse({
            'success': True,
            'is_valid': is_valid,
            'message': 'Логин и пароль верны' if is_valid else 'Логин или пароль неверны'
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def delete_lotw_credentials(request):
    """
    Удаление логина и пароля LoTW
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    try:
        profile = RadioProfile.objects.get(user=request.user)
        profile.lotw_user = ''
        profile.lotw_password = ''
        profile.lotw_chk_pass = False
        profile.save()

        return JsonResponse({'success': True})

    except RadioProfile.DoesNotExist:
        return JsonResponse({'error': 'Профиль не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)