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
    Смена пароля пользователя через Django admin
    """
    if not request.user.is_authenticated:
        messages.error(request, 'Вы должны быть авторизованы')
        return redirect('login_page')

    if request.method == 'POST':
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Проверяем старый пароль
        if not request.user.check_password(old_password):
            messages.error(request, 'Неверный текущий пароль')
            return redirect('profile_update')

        # Валидация нового пароля
        if not new_password:
            messages.error(request, 'Новый пароль не может быть пустым')
            return redirect('profile_update')

        if len(new_password) < 8:
            messages.error(request, 'Пароль должен содержать минимум 8 символов')
            return redirect('profile_update')

        if new_password != confirm_password:
            messages.error(request, 'Пароли не совпадают')
            return redirect('profile_update')

        try:
            # Используем Django метод для смены пароля
            request.user.set_password(new_password)
            request.user.save()

            # Обновляем сессию пользователя чтобы он оставался авторизованным
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)

            messages.success(request, 'Пароль успешно изменён')
            return redirect('profile_update')
        except Exception as e:
            messages.error(request, f'Ошибка при изменении пароля: {str(e)}')
            return redirect('profile_update')

    # Если GET запрос, просто перенаправляем на профиль
    return redirect('profile_update')


def verify_lotw_credentials(request):
    """
    Проверка учетных данных LoTW
    """
    if not request.user.is_authenticated:
        return redirect('login_page')

    # Проверяем, не заблокирован ли пользователь
    is_blocked, reason = check_user_blocked(request.user)
    if is_blocked:
        return render(request, 'blocked.html', {'reason': reason})

    if request.method == 'POST':
        try:
            lotw_user = request.POST.get('lotw_user', '').strip()
            lotw_password = request.POST.get('lotw_password', '').strip()

            if not lotw_user or not lotw_password:
                messages.error(request, 'Логин и пароль LoTW не могут быть пустыми')
                return redirect('profile_update')

            # Получаем или создаем профиль
            try:
                profile = RadioProfile.objects.get(user=request.user)
            except RadioProfile.DoesNotExist:
                profile = RadioProfile.objects.create(user=request.user)

            # Здесь должна быть реальная проверка LoTW
            # Пока что просто проверяем формат позывного и сохраняем флаг как проверенный
            # В реальном проекте здесь был бы запрос к API LoTW
            
            callsign_pattern = r'^[A-Z0-9]{1,3}[0-9][A-Z0-9]{0,3}[A-Z]$'
            if re.match(callsign_pattern, lotw_user.upper()):
                # Сохраняем данные LoTW
                profile.lotw_user = lotw_user.upper()
                profile.lotw_password = lotw_password
                profile.lotw_chk_pass = True  # Устанавливаем флаг проверки
                profile.save(update_fields=['lotw_user', 'lotw_password', 'lotw_chk_pass'])
                
                messages.success(request, f'Учетные данные LoTW для позывного {lotw_user} успешно проверены и сохранены')
            else:
                messages.error(request, 'Неверный формат позывного. Используйте только буквы и цифры (например: UA1ABC)')

        except Exception as e:
            messages.error(request, f'Ошибка при проверке учетных данных LoTW: {str(e)}')

    return redirect('profile_update')


def delete_lotw_credentials(request):
    """
    Удаление учетных данных LoTW
    """
    if not request.user.is_authenticated:
        return redirect('login_page')

    # Проверяем, не заблокирован ли пользователь
    is_blocked, reason = check_user_blocked(request.user)
    if is_blocked:
        return render(request, 'blocked.html', {'reason': reason})

    if request.method == 'POST':
        try:
            # Получаем или создаем профиль
            try:
                profile = RadioProfile.objects.get(user=request.user)
            except RadioProfile.DoesNotExist:
                profile = RadioProfile.objects.create(user=request.user)

            # Очищаем данные LoTW
            profile.lotw_user = ''
            profile.lotw_password = ''
            profile.lotw_chk_pass = False
            profile.lotw_lastsync = None
            profile.save(update_fields=['lotw_user', 'lotw_password', 'lotw_chk_pass', 'lotw_lastsync'])

            messages.success(request, 'Учетные данные LoTW успешно удалены')

        except Exception as e:
            messages.error(request, f'Ошибка при удалении учетных данных LoTW: {str(e)}')

    return redirect('profile_update')