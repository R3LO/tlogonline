# Функции профиля пользователя

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
import json
import re
from ..models import RadioProfile, check_user_blocked


def profile_update(request):
    """
    Обновление профиля радиолюбителя (Django 5.2)
    """
    import json
    
    if not request.user.is_authenticated:
        return redirect('login_page')

    # Проверяем, не заблокирован ли пользователь
    is_blocked, reason = check_user_blocked(request.user)
    if is_blocked:
        return render(request, 'blocked.html', {'reason': reason})

    # Получаем или создаем профиль
    try:
        profile = RadioProfile.objects.get(user=request.user)
    except RadioProfile.DoesNotExist:
        profile = RadioProfile.objects.create(user=request.user)

    if request.method == 'POST':
        try:
            
            # Обновляем поля профиля (callsign всегда равен username)
            profile.callsign = request.user.username.upper()
            profile.first_name = request.POST.get('first_name', '').strip()
            profile.last_name = request.POST.get('last_name', '').strip()
            profile.qth = request.POST.get('qth', '').strip()
            profile.my_gridsquare = request.POST.get('my_gridsquare', '').strip().upper()

            # Обновляем email пользователя
            new_email = request.POST.get('email', '').strip()
            if new_email:
                # Простая валидация email - не прерываем сохранение если email неверный
                email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
                if re.match(email_pattern, new_email):
                    request.user.email = new_email
                    request.user.save(update_fields=['email'])
                else:
                    # Показываем предупреждение, но не прерываем сохранение
                    messages.warning(request, 'Введённый email адрес может быть некорректным, но данные профиля сохранены')
            else:
                # Если email пустой, очищаем его
                request.user.email = ''
                request.user.save(update_fields=['email'])

            # Обработка настроек LoTW
            use_lotw = 'use_lotw' in request.POST
            if use_lotw:
                profile.lotw_user = request.POST.get('lotw_user', '').strip()
                profile.lotw_password = request.POST.get('lotw_password', '').strip()
                # lotw_chk_pass сохраняется как есть (обновляется при проверке)
            else:
                # Очищаем данные LoTW если чекбокс не выбран
                profile.lotw_user = ''
                profile.lotw_password = ''
                profile.lotw_chk_pass = False

            # Обрабатываем my_callsigns из JSON (новый формат: простой список строк)
            my_callsigns_json = request.POST.get('my_callsigns_json', '[]')
            try:
                new_my_callsigns = json.loads(my_callsigns_json)
                
                # Преобразуем список объектов в простой список строк (если нужно)
                if new_my_callsigns and isinstance(new_my_callsigns, list):
                    if isinstance(new_my_callsigns[0], dict):
                        # Старый формат: [{'name': 'CALL1'}, {'name': 'CALL2'}]
                        new_my_callsigns = [item['name'] for item in new_my_callsigns if item.get('name')]
                    
            except json.JSONDecodeError as e:
                new_my_callsigns = []

            # Всегда сохраняем my_callsigns и LoTW данные
            profile.lotw_lastsync = None
            profile.my_callsigns = new_my_callsigns
            profile.save(update_fields=['lotw_lastsync', 'my_callsigns', 'lotw_user', 'lotw_password', 'lotw_chk_pass'])

            # Также обновляем User модель
            request.user.first_name = profile.first_name
            request.user.last_name = profile.last_name
            request.user.save(update_fields=['first_name', 'last_name'])

            messages.success(request, 'Профиль успешно обновлён')
            return redirect('profile_update')
        except Exception as e:
            messages.error(request, f'Ошибка при обновлении профиля: {str(e)}')

    # Для GET запроса или после POST с ошибкой - показываем форму
    # Добавляем JSON данные в контекст для JavaScript (простой список строк)
    import json
    profile_json = json.dumps(profile.my_callsigns, ensure_ascii=False)
    
    return render(request, 'profile_edit.html', {
        'profile': profile,
        'profile_json': profile_json,
    })


def change_password(request):
    """
    Смена пароля пользователя
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Вы должны быть авторизованы'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    try:
        data = json.loads(request.body)
        new_password = data.get('password', '')

        if not new_password:
            return JsonResponse({'error': 'Пароль не может быть пустым'}, status=400)

        if len(new_password) < 8:
            return JsonResponse({'error': 'Пароль должен содержать минимум 8 символов'}, status=400)

        # Устанавливаем новый пароль через set_password (Django автоматически хеширует)
        request.user.set_password(new_password)
        request.user.save()

        # Разлогиниваем пользователя и перенаправляем на страницу логина
        from django.contrib.auth import logout
        logout(request)

        return JsonResponse({
            'success': True,
            'message': 'Пароль успешно изменён',
            'redirect': '/login/'
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)