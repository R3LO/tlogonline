# Функции профиля пользователя

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
import json
import re
import requests
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
            # Получаем данные из формы
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            qth = request.POST.get('qth', '').strip()
            my_gridsquare = request.POST.get('my_gridsquare', '').strip().upper()
            
            print(f"🔍 Получены данные формы:")
            print(f"   first_name: '{first_name}'")
            print(f"   last_name: '{last_name}'")
            print(f"   qth: '{qth}'")
            print(f"   my_gridsquare: '{my_gridsquare}'")
            
            # Обновляем поля профиля (callsign всегда равен username)
            profile.callsign = request.user.username.upper()
            profile.first_name = first_name
            profile.last_name = last_name
            profile.qth = qth
            profile.my_gridsquare = my_gridsquare

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
            lotw_user = request.POST.get('lotw_user', '').strip()
            lotw_password = request.POST.get('lotw_password', '').strip()
            
            # Сохраняем данные LoTW если они введены
            if lotw_user or lotw_password:
                profile.lotw_user = lotw_user
                profile.lotw_password = lotw_password
                # lotw_chk_pass сохраняется как есть (обновляется при проверке)
            else:
                # Очищаем данные LoTW если поля пустые
                profile.lotw_user = ''
                profile.lotw_password = ''
                profile.lotw_chk_pass = False

            # Обрабатываем my_callsigns из JSON (новый формат: простой список строк)
            my_callsigns_json = request.POST.get('my_callsigns_json', '[]')
            print(f"📡 Получены данные позывных JSON: {my_callsigns_json}")
            
            try:
                new_my_callsigns = json.loads(my_callsigns_json)
                print(f"📡 Распарсенные позывные: {new_my_callsigns}")
                
                # Нормализуем данные позывных - простая очистка без строгой валидации
                if new_my_callsigns and isinstance(new_my_callsigns, list):
                    # Убираем дубликаты и пустые значения, приводим к верхнему регистру
                    normalized_callsigns = []
                    for callsign in new_my_callsigns:
                        if isinstance(callsign, str) and callsign.strip():
                            callsign_clean = callsign.strip().upper()
                            if callsign_clean not in normalized_callsigns:
                                # Базовая проверка - только латинские буквы, цифры и слеш
                                if re.match(r'^[A-Z0-9\/]+$', callsign_clean):
                                    normalized_callsigns.append(callsign_clean)
                    
                    new_my_callsigns = normalized_callsigns
                    print(f"✅ Нормализованные позывные: {new_my_callsigns}")
                else:
                    new_my_callsigns = []
                    print(f"ℹ️ Позывные пустые или не список")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Ошибка парсинга JSON позывных: {e}")
                new_my_callsigns = []

            # ===== ВАЛИДАЦИЯ: Если LoTW настроен (проверен), должны быть позывные =====
            # Проверяем: если lotw_chk_pass=True (уже проверен ранее) и нет позывных - ошибка
            if profile.lotw_chk_pass and (not new_my_callsigns or len(new_my_callsigns) == 0):
                messages.error(request, '❌ Добавьте хотя бы один позывной синхронизации для LoTW')
                return render(request, 'profile_edit.html', {
                    'profile': profile,
                    'profile_json': json.dumps(profile.my_callsigns, ensure_ascii=False),
                })

            # Устанавливаем данные профиля
            profile.lotw_lastsync = None
            profile.my_callsigns = new_my_callsigns

            print(f"💾 Сохраняем позывные в профиль: {new_my_callsigns}")

            # Сохраняем профиль с основными полями
            profile.save()

            print(f"✅ Профиль сохранён. Позывные в базе: {profile.my_callsigns}")

            # Обновляем User модель с данными из формы
            request.user.first_name = first_name
            request.user.last_name = last_name
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
    print(f"🔐 Функция change_password вызвана. Method: {request.method}")
    
    if not request.user.is_authenticated:
        print(f"❌ Пользователь не авторизован")
        messages.error(request, 'Вы должны быть авторизованы')
        return redirect('login_page')

    print(f"✅ Пользователь авторизован: {request.user.username}")

    if request.method == 'POST':
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        print(f"📝 Получены данные для смены пароля:")
        print(f"   old_password: {'*' * len(old_password) if old_password else 'ПУСТОЙ'}")
        print(f"   new_password: {'*' * len(new_password) if new_password else 'ПУСТОЙ'}")
        print(f"   confirm_password: {'*' * len(confirm_password) if confirm_password else 'ПУСТОЙ'}")

        # Проверяем старый пароль
        if not old_password:
            print(f"❌ Текущий пароль не введен")
            messages.error(request, 'Введите текущий пароль')
            return redirect('profile_update')

        if not request.user.check_password(old_password):
            print(f"❌ Неверный текущий пароль")
            messages.error(request, 'Неверный текущий пароль')
            return redirect('profile_update')

        print(f"✅ Текущий пароль верный")

        # Валидация нового пароля
        if not new_password:
            print(f"❌ Новый пароль не введен")
            messages.error(request, 'Новый пароль не может быть пустым')
            return redirect('profile_update')

        if len(new_password) < 8:
            print(f"❌ Слишком короткий пароль: {len(new_password)} символов")
            messages.error(request, 'Пароль должен содержать минимум 8 символов')
            return redirect('profile_update')

        if new_password != confirm_password:
            print(f"❌ Пароли не совпадают")
            messages.error(request, 'Пароли не совпадают')
            return redirect('profile_update')

        print(f"✅ Валидация пройдена, сохраняем новый пароль...")

        try:
            # Используем Django метод для смены пароля
            request.user.set_password(new_password)
            request.user.save()
            print(f"✅ Пароль успешно сохранен в базе данных")

            # Обновляем сессию пользователя чтобы он оставался авторизованным
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            print(f"✅ Сессия пользователя обновлена")

            messages.success(request, '✅ Пароль успешно изменён')
            return redirect('profile_update')
        except Exception as e:
            print(f"❌ Ошибка при изменении пароля: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Ошибка при изменении пароля: {str(e)}')
            return redirect('profile_update')

    # Если GET запрос, просто перенаправляем на профиль
    print(f"ℹ️ GET запрос, перенаправляем на профиль")
    return redirect('profile_update')


def verify_lotw_credentials(request):
    """
    Проверка логина и пароля LoTW с реальным API запросом
    """
    if request.method != 'POST':
        messages.error(request, 'Метод не поддерживается')
        return redirect('profile_update')

    try:
        # Получаем логин и пароль из POST данных
        login = request.POST.get('lotw_user', '').strip()
        password = request.POST.get('lotw_password', '').strip()

        if not login or not password:
            messages.error(request, 'Логин и пароль обязательны')
            return redirect('profile_update')

        # Функция проверки LoTW через API
        def check_lotw_pass(login, password):
            params = {
                'login': login,
                'password': password,
            }
            try:
                response = requests.get(
                    "https://lotw.arrl.org/lotwuser/lotwreport.adi",
                    params=params,
                    timeout=15
                )
                
                print(f"🔍 LoTW API Response Status: {response.status_code}")
                print(f"🔍 LoTW API Response Headers: {dict(response.headers)}")
                print(f"🔍 LoTW API Response Content (first 500 chars): {response.text[:500]}")
                
                # Проверяем ответ LoTW API по содержанию
                response_text = response.text.strip()
                
                # Успешный ответ содержит статусный отчет LoTW
                if response_text.startswith('ARRL Logbook of the World Status Report'):
                    print("✅ Успешный ответ от LoTW API")
                    return True, "success"
                
                # Неверные учетные данные - HTML страница с ошибкой
                elif '<HTML>' in response_text.upper() or '<!DOCTYPE HTML' in response_text.upper():
                    print("❌ Получен HTML ответ - неверные учетные данные")
                    return False, "invalid_credentials"
                
                # HTTP ошибка
                elif response.status_code != 200:
                    print(f"❌ HTTP ошибка: {response.status_code}")
                    return False, "http_error"
                
                # Неожиданный ответ - возможно неверный пароль или проблема с сервером
                else:
                    print("❌ Неожиданный ответ от LoTW API")
                    # Сохраняем ответ для отладки
                    print(f"📝 Полный ответ: {response_text}")
                    return False, "unexpected_response"
                    
            except requests.RequestException as e:
                print(f"❌ Ошибка при запросе к LoTW API: {e}")
                return False, "network_error"

        # Выполняем проверку
        is_valid, error_type = check_lotw_pass(login, password)

        # Обновляем профиль пользователя
        try:
            profile = RadioProfile.objects.get(user=request.user)
            
            if is_valid:
                # Успешная проверка
                profile.lotw_chk_pass = True
                profile.lotw_user = login
                profile.lotw_password = password
                profile.save(update_fields=['lotw_chk_pass', 'lotw_user', 'lotw_password'])
                messages.success(request, '✅ Логин и пароль проверены и сохранены успешно')
                
            else:
                # Неверная проверка - сохраняем данные, но сбрасываем флаг проверки
                profile.lotw_chk_pass = False
                profile.lotw_user = login  # Сохраняем введенные данные
                profile.lotw_password = password  # Сохраняем введенные данные
                profile.save(update_fields=['lotw_chk_pass', 'lotw_user', 'lotw_password'])
                
                # Разные сообщения в зависимости от типа ошибки
                if error_type == "invalid_credentials":
                    messages.error(request, '❌ LoTW: Логин или пароль неверны. Проверьте данные и попробуйте снова.')
                elif error_type == "http_error":
                    messages.error(request, '❌ LoTW: Ошибка сервера. Попробуйте позже.')
                elif error_type == "network_error":
                    messages.error(request, '❌ LoTW: Ошибка соединения. Проверьте интернет и попробуйте снова.')
                elif error_type == "unexpected_response":
                    messages.error(request, '❌ LoTW: Неожиданный ответ. Проверьте логин и пароль, затем попробуйте снова.')
                else:
                    messages.error(request, '❌ LoTW: Ошибка при проверке данных. Попробуйте снова.')
                    
        except RadioProfile.DoesNotExist:
            messages.error(request, 'Профиль пользователя не найден')
            
        return redirect('profile_update')

    except Exception as e:
        messages.error(request, f'Ошибка при проверке: {str(e)}')
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