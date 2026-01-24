"""
Основные представления (главная страница, личный кабинет, профиль)
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import json
from ..models import QSO, RadioProfile, ADIFUpload, check_user_blocked, ChatMessage


def home(request):
    """
    Главная страница
    """
    total_users = User.objects.count()
    total_qso = QSO.objects.count()

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


def dashboard(request):
    """
    Личный кабинет радиолюбителя
    """
    if not request.user.is_authenticated:
        return redirect('login_page')

    # Проверяем, не заблокирован ли пользователь
    is_blocked, reason = check_user_blocked(request.user)
    if is_blocked:
        return render(request, 'blocked.html', {'reason': reason})

    # Обработка формы ручного ввода QSO
    if request.method == 'POST' and request.POST.get('action') == 'add_qso':
        try:
            from datetime import date, time
            from django.db.utils import IntegrityError

            # Получаем данные из формы
            my_callsign = request.POST.get('my_callsign', '').strip().upper()
            callsign = request.POST.get('callsign', '').strip().upper()
            date_str = request.POST.get('date', '').strip()
            time_str = request.POST.get('time', '').strip()
            band = request.POST.get('band', '').strip().upper()
            mode = request.POST.get('mode', '').strip().upper()
            rst_rcvd = request.POST.get('rst_rcvd', '').strip().upper()
            rst_sent = request.POST.get('rst_sent', '').strip().upper()
            gridsquare = request.POST.get('gridsquare', '').strip().upper()
            ru_region = request.POST.get('ru_region', '').strip().upper()

            # Валидация обязательных полей
            if not all([my_callsign, callsign, date_str, time_str, band, mode]):
                messages.error(request, 'Все обязательные поля должны быть заполнены')
                return redirect('dashboard')

            # Валидация форматов
            if len(my_callsign) > 20 or len(callsign) > 20:
                messages.error(request, 'Позывной не должен превышать 20 символов')
                return redirect('dashboard')

            if len(gridsquare) > 8:
                messages.error(request, 'QTH локатор не должен превышать 8 символов')
                return redirect('dashboard')

            # Парсинг даты и времени
            try:
                qso_date = date.fromisoformat(date_str)
                qso_time = time.fromisoformat(time_str)
            except ValueError:
                messages.error(request, 'Неверный формат даты или времени')
                return redirect('dashboard')

            # Проверка на дубликат
            duplicate_exists = QSO.objects.filter(
                user=request.user,
                my_callsign=my_callsign,
                callsign=callsign,
                date=qso_date,
                time=qso_time,
                band=band,
                mode=mode
            ).exists()

            if duplicate_exists:
                messages.warning(request, 'QSO с такими данными уже существует в логе')
                return redirect('dashboard')

            # Определение частоты по диапазону (упрощенное сопоставление)
            band_frequencies = {
                '160m': 1.9, '80m': 3.7, '40m': 7.1, '30m': 10.15, '20m': 14.2,
                '17m': 18.12, '15m': 21.3, '12m': 24.95, '10m': 28.5, '6m': 52.0,
                '2m': 144.0, '70cm': 435.0, '23cm': 1290.0, '13cm': 2400.0, '3cm': 10000.0
            }

            frequency = band_frequencies.get(band, 0.0)

            # Создание записи QSO
            try:
                QSO.objects.create(
                    user=request.user,
                    my_callsign=my_callsign,
                    callsign=callsign,
                    date=qso_date,
                    time=qso_time,
                    frequency=frequency,
                    band=band,
                    mode=mode,
                    rst_rcvd=rst_rcvd if rst_rcvd else None,
                    rst_sent=rst_sent if rst_sent else None,
                    gridsquare=gridsquare if gridsquare else None,
                    ru_region=ru_region if ru_region else None,
                    lotw='N',
                    paper_qsl='N'
                )

                messages.success(request, f'QSO с {callsign} успешно добавлено в лог')
                return redirect('dashboard')

            except IntegrityError as e:
                messages.error(request, f'Ошибка при сохранении QSO: {str(e)}')
                return redirect('dashboard')

        except Exception as e:
            messages.error(request, f'Ошибка при обработке формы: {str(e)}')
            return redirect('dashboard')

    # Получаем профиль радиолюбителя
    try:
        profile = request.user.radio_profile
    except RadioProfile.DoesNotExist:
        profile = None

    # Получаем QSO пользователя
    user_qso = QSO.objects.filter(user=request.user)

    # Подсчитываем статистику
    total_qso = user_qso.count()
    unique_callsigns = user_qso.values('callsign').distinct().count()

    # Статистика по DXCC (страны)
    dxcc_count = user_qso.exclude(dxcc__isnull=True).exclude(dxcc='').values('dxcc').distinct().count()

    # Статистика по Р-150-С (регионы России)
    r150s_count = user_qso.exclude(r150s__isnull=True).exclude(r150s='').values('r150s').distinct().count()

    # Статистика по регионам России (ru_region)
    ru_region_count = user_qso.exclude(ru_region__isnull=True).exclude(ru_region='').values('ru_region').distinct().count()

    # Статистика по видам модуляции
    mode_stats = {}
    mode_choices = dict(QSO._meta.get_field('mode').choices)
    for mode in mode_choices.keys():
        count = user_qso.filter(mode=mode).count()
        if count > 0:
            mode_stats[mode] = count

    # Последние QSO (последние 10)
    recent_qso = user_qso.order_by('-date', '-time')[:10]

    # Получаем загруженные ADIF файлы
    adif_uploads = ADIFUpload.objects.filter(user=request.user).order_by('-upload_date')[:5]

    context = {
        'user': request.user,
        'profile': profile,
        'total_qso': total_qso,
        'unique_callsigns': unique_callsigns,
        'dxcc_count': dxcc_count,
        'r150s_count': r150s_count,
        'ru_region_count': ru_region_count,
        'recent_qso': recent_qso,
        'mode_statistics': mode_stats,
        'adif_uploads': adif_uploads,
    }

    return render(request, 'dashboard.html', context)


def profile_update(request):
    """
    Обновление профиля радиолюбителя (Django 5.2)
    """
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
                # Простая валидация email
                import re
                email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
                if re.match(email_pattern, new_email):
                    request.user.email = new_email
                    request.user.save(update_fields=['email'])
                else:
                    messages.error(request, 'Введите корректный email адрес')
                    return render(request, 'profile_edit.html', {
                        'profile': profile,
                    })

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

            # Обрабатываем my_callsigns из JSON
            my_callsigns_json = request.POST.get('my_callsigns_json', '[]')
            try:
                new_my_callsigns = json.loads(my_callsigns_json)
            except json.JSONDecodeError:
                new_my_callsigns = []

            # Проверяем, изменились ли my_callsigns
            old_my_callsigns = profile.my_callsigns if profile.my_callsigns else []
            if isinstance(old_my_callsigns, str):
                old_my_callsigns = json.loads(old_my_callsigns)

            # Если изменились - очищаем lotw_lastsync
            if old_my_callsigns != new_my_callsigns:
                profile.lotw_lastsync = None
                profile.my_callsigns = new_my_callsigns
                profile.save(update_fields=['lotw_lastsync', 'my_callsigns'])
            else:
                profile.my_callsigns = new_my_callsigns
                profile.save()

            # Также обновляем User модель
            request.user.first_name = profile.first_name
            request.user.last_name = profile.last_name
            request.user.save(update_fields=['first_name', 'last_name'])

            messages.success(request, 'Профиль успешно обновлён')
            return redirect('profile_update')
        except Exception as e:
            messages.error(request, f'Ошибка при обновлении профиля: {str(e)}')

    # Для GET запроса или после POST с ошибкой - показываем форму
    return render(request, 'profile_edit.html', {
        'profile': profile,
    })


def verify_lotw_credentials(request):
    """
    Проверка логина и пароля LoTW
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Вы должны быть авторизованы'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    try:
        import requests

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


def delete_lotw_credentials(request):
    """
    Удаление логина и пароля LoTW
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Вы должны быть авторизованы'}, status=403)

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


def chat_list(request):
    """
    Получение списка последних сообщений чата (для AJAX)
    """
    # Получаем последние 100 сообщений
    messages = ChatMessage.objects.all()[:100]

    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': str(msg.id),
            'user_id': msg.user.id,
            'username': msg.username,
            'message': msg.message,
            'created_at': msg.created_at.strftime('%H:%M'),
        })

    return JsonResponse({'messages': messages_data})


def chat_send(request):
    """
    Отправка нового сообщения в чат
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Вы должны быть авторизованы'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    try:
        import json
        data = json.loads(request.body)
        message_text = data.get('message', '').strip()

        if not message_text:
            return JsonResponse({'error': 'Сообщение не может быть пустым'}, status=400)

        if len(message_text) > 500:
            return JsonResponse({'error': 'Сообщение слишком длинное (максимум 500 символов)'}, status=400)

        # Получаем callsign пользователя
        try:
            profile = request.user.radio_profile
            username = profile.callsign or request.user.username
        except RadioProfile.DoesNotExist:
            username = request.user.username

        # Создаем сообщение
        chat_message = ChatMessage.objects.create(
            user=request.user,
            username=username,
            message=message_text
        )

        # Удаляем старые сообщения, оставляем только последние 100
        # Получаем ID последних 100 сообщений
        keep_ids = list(ChatMessage.objects.order_by('-created_at')[:100].values_list('id', flat=True))
        # Удаляем все остальные
        ChatMessage.objects.exclude(id__in=keep_ids).delete()

        return JsonResponse({
            'success': True,
            'message': {
                'id': str(chat_message.id),
                'username': chat_message.username,
                'message': chat_message.message,
                'created_at': chat_message.created_at.strftime('%H:%M'),
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def custom_404_view(request, exception):
    """
    Обработчик ошибки 404 - страница не найдена
    """
    return render(request, '404.html', {
        'request_path': request.path,
    }, status=404)