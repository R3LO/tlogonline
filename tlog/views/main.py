"""
Основные представления (главная страница, личный кабинет, профиль)
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from ..models import QSO, RadioProfile, ADIFUpload, check_user_blocked


def home(request):
    """
    Главная страница
    """
    return render(request, 'index.html')


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

    # Последние QSO (последние 20)
    recent_qso = user_qso.order_by('-date', '-time')[:20]

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