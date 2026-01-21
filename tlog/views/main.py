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

    # Получаем уникальные позывные из QSO (убираем дубликаты через set)
    callsigns = list(set(QSO.objects.filter(
        my_callsign__icontains=query
    ).values_list('my_callsign', flat=True).distinct()[:10]))

    return JsonResponse({'callsigns': callsigns})


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
            my_callsign = request.POST.get('my_callsign', '').strip()
            callsign = request.POST.get('callsign', '').strip()
            date_str = request.POST.get('date', '').strip()
            time_str = request.POST.get('time', '').strip()
            band = request.POST.get('band', '').strip()
            mode = request.POST.get('mode', '').strip()
            rst_rcvd = request.POST.get('rst_rcvd', '').strip()
            rst_sent = request.POST.get('rst_sent', '').strip()
            gridsquare = request.POST.get('gridsquare', '').strip()
            ru_region = request.POST.get('ru_region', '').strip()

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
        'recent_qso': recent_qso,
        'mode_statistics': mode_stats,
        'adif_uploads': adif_uploads,
    }

    return render(request, 'dashboard.html', context)


def profile_update(request):
    """
    Обновление профиля радиолюбителя
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
            profile, created = RadioProfile.objects.get_or_create(
                user=request.user,
                defaults={}
            )

            # Обновляем поля профиля
            profile.callsign = request.POST.get('callsign', '').strip()
            profile.full_name = request.POST.get('full_name', '').strip()
            profile.qth = request.POST.get('qth', '').strip()
            profile.my_gridsquare = request.POST.get('my_gridsquare', '').strip().upper()

            profile.save()

            messages.success(request, 'Профиль успешно обновлён')
        except Exception as e:
            messages.error(request, f'Ошибка при обновлении профиля: {str(e)}')

    return redirect('dashboard')


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