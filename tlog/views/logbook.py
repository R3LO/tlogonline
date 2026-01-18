"""
Представления для работы с журналом QSO
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from ..models import QSO, RadioProfile, ADIFUpload, LogbookComment, LogbookComment


def get_band_from_frequency(frequency):
    """
    Определяет диапазон по частоте
    """
    if frequency is None:
        return 'Unknown'

    band_ranges = {
        '160m': (1.8, 2.0), '80m': (3.5, 4.0), '40m': (7.0, 7.3), '30m': (10.1, 10.15),
        '20m': (14.0, 14.35), '17m': (18.068, 18.168), '15m': (21.0, 21.45),
        '12m': (24.89, 24.99), '10m': (28.0, 29.7), '6m': (50.0, 54.0),
        '4m': (70.0, 70.5), '2m': (144.0, 148.0), '70cm': (420.0, 450.0),
        '23cm': (1240.0, 1300.0), '13cm': (2400.0, 2500.0),
    }

    for band, (min_freq, max_freq) in band_ranges.items():
        if min_freq <= frequency <= max_freq:
            return band

    return f"{frequency:.1f}MHz"


def logbook(request):
    """
    Журнал QSO с поиском и фильтрацией
    """
    if not request.user.is_authenticated:
        return redirect('login_page')

    # Получаем параметры фильтрации
    search_callsign = request.GET.get('search_callsign', '').strip()
    search_qth = request.GET.get('search_qth', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    mode_filter = request.GET.get('mode', '').strip()
    band_filter = request.GET.get('band', '').strip()
    sat_name_filter = request.GET.get('sat_name', '').strip()
    lotw_filter = request.GET.get('lotw', '').strip()

    # Базовый QuerySet для QSO пользователя
    qso_queryset = QSO.objects.filter(user=request.user)

    # Применяем поиск по части позывного
    if search_callsign:
        qso_queryset = qso_queryset.filter(callsign__icontains=search_callsign)

    # Применяем поиск по части QTH локатора
    if search_qth:
        qso_queryset = qso_queryset.filter(gridsquare__icontains=search_qth)

    # Фильтр по дате "с"
    if date_from:
        qso_queryset = qso_queryset.filter(date__gte=date_from)

    # Фильтр по дате "до"
    if date_to:
        qso_queryset = qso_queryset.filter(date__lte=date_to)

    # Применяем фильтры
    if mode_filter:
        qso_queryset = qso_queryset.filter(mode=mode_filter)

    # Фильтр по диапазону - напрямую по полю band
    if band_filter:
        qso_queryset = qso_queryset.filter(band=band_filter)

    # Фильтр по SAT NAME
    if sat_name_filter:
        qso_queryset = qso_queryset.filter(sat_name=sat_name_filter)

    # Фильтр по LoTW
    if lotw_filter:
        qso_queryset = qso_queryset.filter(lotw=lotw_filter)

    # Сортируем по дате (новые сверху)
    qso_queryset = qso_queryset.order_by('-date', '-time')

    # Пагинация (50 записей на страницу)
    page_size = 50
    page = int(request.GET.get('page', 1))
    start = (page - 1) * page_size
    end = start + page_size

    qso_list = qso_queryset[start:end]
    total_count = qso_queryset.count()
    total_pages = (total_count + page_size - 1) // page_size

    # Уникальные значения для фильтров
    unique_modes = qso_queryset.values_list('mode', flat=True).distinct().order_by('mode')
    unique_bands = qso_queryset.values_list('band', flat=True).distinct().exclude(band__isnull=True).exclude(band='').order_by('band')
    unique_sat_names = qso_queryset.values_list('sat_name', flat=True).distinct().exclude(sat_name__isnull=True).exclude(sat_name='').order_by('sat_name')

    # Статистика для выбранных фильтров
    filtered_stats = {
        'total_qso': total_count,
        'unique_callsigns': qso_queryset.values('callsign').distinct().count(),
        'unique_dxcc': qso_queryset.filter(state__isnull=False).exclude(state='').values('state').distinct().count(),
        'unique_r150s': qso_queryset.filter(r150s__isnull=False).exclude(r150s='').values('r150s').distinct().count(),
    }

    # Статистика по диапазонам
    band_stats = {}
    bands = ['160m', '80m', '40m', '20m', '15m', '10m', '6m', '2m', '70cm', '23cm', '13cm']
    band_ranges = {
        '160m': (1.8, 2.0), '80m': (3.5, 4.0), '40m': (7.0, 7.3), '30m': (10.1, 10.15),
        '20m': (14.0, 14.35), '17m': (18.068, 18.168), '15m': (21.0, 21.45),
        '12m': (24.89, 24.99), '10m': (28.0, 29.7), '6m': (50.0, 54.0),
        '4m': (70.0, 70.5), '2m': (144.0, 148.0), '70cm': (420.0, 450.0),
        '23cm': (1240.0, 1300.0), '13cm': (2400.0, 2500.0),
    }

    for band in bands:
        if band in band_ranges:
            min_freq, max_freq = band_ranges[band]
            count = qso_queryset.filter(frequency__gte=min_freq, frequency__lte=max_freq).count()
            if count > 0:
                band_stats[band] = count

    # Позывной пользователя из профиля
    try:
        user_callsign = request.user.radio_profile.callsign
    except RadioProfile.DoesNotExist:
        user_callsign = request.user.username

    context = {
        'user': request.user,
        'user_callsign': user_callsign,
        'qso_list': qso_list,
        'total_count': total_count,
        'current_page': page,
        'total_pages': total_pages,
        'page_size': page_size,
        'search_callsign': search_callsign,
        'search_qth': search_qth,
        'date_from': date_from,
        'date_to': date_to,
        'mode_filter': mode_filter,
        'band_filter': band_filter,
        'sat_name_filter': sat_name_filter,
        'lotw_filter': lotw_filter,
        'available_modes': unique_modes,
        'available_bands': unique_bands,
        'available_sat_names': unique_sat_names,
        'filtered_stats': filtered_stats,
        'band_stats': band_stats,
        'get_band_from_frequency': get_band_from_frequency,
    }

    return render(request, 'logbook.html', context)


def logbook_search(request, callsign):
    """
    Поиск по логам пользователя по позывному.
    """
    # Нормализуем позывной
    callsign = callsign.strip().upper()
    has_logs = QSO.objects.filter(my_callsign=callsign).exists()

    if not has_logs:
        return render(request, 'logbook_search.html', {
            'callsign': callsign,
            'has_logs': False,
            'error_message': f'Лог с позывным "{callsign}" не найден в базе данных.',
        })

    search_callsign = request.GET.get('callsign', '').strip()

    # Получаем комментарии для этого лога (новые сверху)
    comments = LogbookComment.objects.filter(callsign=callsign)[:20]

    # Базовый queryset для всех QSO этого лога
    base_queryset = QSO.objects.filter(my_callsign=callsign)

    # Диапазоны и моды для матрицы
    bands = ['160m', '80m', '40m', '30m', '20m', '17m', '15m', '12m', '10m', '6m', '2m', '70cm', '23cm', '13cm']
    modes = ['CW', 'SSB', 'FT8', 'FT4', 'RTTY', 'SSTV', 'MFSK', 'JT65', 'JT9', 'PSK31', 'AM', 'FM', 'DIG']

    band_ranges = {
        '160m': (1.8, 2.0), '80m': (3.5, 4.0), '40m': (7.0, 7.3), '30m': (10.1, 10.15),
        '20m': (14.0, 14.35), '17m': (18.068, 18.168), '15m': (21.0, 21.45),
        '12m': (24.89, 24.99), '10m': (28.0, 29.7), '6m': (50.0, 54.0),
        '2m': (144.0, 148.0), '70cm': (420.0, 450.0), '23cm': (1240.0, 1300.0),
        '13cm': (2300.0, 2450.0),  # Расширенный диапазон для 13cm
    }

    # Фильтруем по позывному корреспондента если задан
    if search_callsign:
        qso_queryset = base_queryset.filter(callsign__icontains=search_callsign).order_by('-date', '-time')
    else:
        qso_queryset = base_queryset.order_by('-date', '-time')

    total_qso = qso_queryset.count()

    # Формируем матрицу mode x band - используем поле band из базы
    # Формат: [[mode, band1_has, band2_has, ...], ...]
    matrix = []
    for mode in modes:
        row = [mode]
        for band in bands:
            count = qso_queryset.filter(
                Q(mode__iexact=mode) &
                (Q(band=band) | Q(frequency__gte=band_ranges[band][0], frequency__lte=band_ranges[band][1]))
            ).count()
            row.append(count > 0)
        matrix.append(row)

    # Пагинация для детальной таблицы
    page = int(request.GET.get('page', 1))
    page_size = 50
    start = (page - 1) * page_size
    end = start + page_size
    total_pages = (total_qso + page_size - 1) // page_size if total_qso > 0 else 1

    context = {
        'callsign': callsign,
        'has_logs': True,
        'search_callsign': search_callsign,
        'qso_list': qso_queryset[start:end],
        'comments': comments,
        'total_qso': total_qso,
        'matrix': matrix,
        'bands': bands,
        'modes': modes,
        'current_page': page,
        'total_pages': total_pages,
    }

    return render(request, 'logbook_search.html', context)


def clear_logbook(request):
    """
    Удаляет все записи QSO и загруженные ADIF файлы пользователя
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        # Подсчитываем количество записей для статистики
        qso_count = QSO.objects.filter(user=request.user).count()
        unique_callsigns = QSO.objects.filter(user=request.user).values('callsign').distinct().count()
        unique_dxcc = QSO.objects.filter(user=request.user).filter(
            state__isnull=False
        ).exclude(state='').values('state').distinct().count()
        unique_r150s = QSO.objects.filter(user=request.user).filter(
            r150s__isnull=False
        ).exclude(r150s='').values('r150s').distinct().count()
        adif_uploads_count = ADIFUpload.objects.filter(user=request.user).count()

        # Удаляем все записи QSO пользователя
        deleted_qso_count, _ = QSO.objects.filter(user=request.user).delete()

        # Удаляем все загруженные ADIF файлы пользователя
        deleted_adif_count, _ = ADIFUpload.objects.filter(user=request.user).delete()

        return JsonResponse({
            'success': True,
            'message': f'Удалено {deleted_qso_count} записей QSO и {deleted_adif_count} записей о загруженных файлах',
            'stats': {
                'deleted_qso': deleted_qso_count,
                'deleted_adif_uploads': deleted_adif_count,
                'unique_callsigns': unique_callsigns,
                'unique_dxcc': unique_dxcc,
                'unique_r150s': unique_r150s
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Ошибка при удалении записей: {str(e)}'
        }, status=500)


@login_required
def edit_qso(request, qso_id):
    """
    Редактирование одной записи QSO
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не разрешён'}, status=405)

    try:
        qso = QSO.objects.get(id=qso_id, user=request.user)
    except (QSO.DoesNotExist, ValueError):
        return JsonResponse({'success': False, 'error': 'Запись не найдена'}, status=404)

    try:
        import json
        data = json.loads(request.body)

        # Обновляем поля записи
        qso.date = data.get('date')
        qso.time = data.get('time')
        qso.callsign = data.get('callsign', '')[:20]
        qso.band = data.get('band', '')[:10] or None
        qso.mode = data.get('mode') or 'SSB'

        frequency = data.get('frequency')
        if frequency:
            try:
                qso.frequency = float(frequency)
            except (ValueError, TypeError):
                qso.frequency = None
        else:
            qso.frequency = None

        qso.rst_rcvd = data.get('rst_rcvd', '')[:10] or None
        qso.rst_sent = data.get('rst_sent', '')[:10] or None
        qso.my_gridsquare = data.get('my_gridsquare', '')[:10] or None
        qso.gridsquare = data.get('gridsquare', '')[:10] or None
        qso.sat_name = data.get('sat_name', '')[:50] or None
        qso.prop_mode = data.get('prop_mode', '')[:50] or None

        cqz = data.get('cqz')
        qso.cqz = int(cqz) if cqz else None

        ituz = data.get('ituz')
        qso.ituz = int(ituz) if ituz else None

        qso.lotw = data.get('lotw', 'N')

        qso.save()

        return JsonResponse({'success': True, 'message': 'Запись успешно обновлена'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def generate_captcha(request):
    """
    Генерация простой математической капчи
    """
    import random
    import uuid

    # Генерируем два случайных числа от 1 до 10
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    answer = a + b

    # Создаём уникальный токен
    token = str(uuid.uuid4())

    # Сохраняем ответ в сессии
    if 'captcha_token' not in request.session:
        request.session['captcha_token'] = {}
    request.session['captcha_token'][token] = answer
    request.session.modified = True

    return JsonResponse({
        'success': True,
        'token': token,
        'question': f'{a} + {b} = ?'
    })


@login_required
def delete_qso(request, qso_id):
    """
    Удаление одной записи QSO
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не разрешён'}, status=405)

    try:
        qso = QSO.objects.get(id=qso_id, user=request.user)
        qso.delete()
        return JsonResponse({'success': True, 'message': 'Запись успешно удалена'})
    except (QSO.DoesNotExist, ValueError):
        return JsonResponse({'success': False, 'error': 'Запись не найдена'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def get_qso(request, qso_id):
    """
    Получение данных одной записи QSO в формате JSON
    """
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Метод не разрешён'}, status=405)

    try:
        qso = QSO.objects.get(id=qso_id, user=request.user)
        return JsonResponse({
            'success': True,
            'qso': {
                'id': str(qso.id),
                'date': qso.date.isoformat() if qso.date else None,
                'time': qso.time.isoformat() if qso.time else None,
                'my_callsign': qso.my_callsign or '',
                'callsign': qso.callsign or '',
                'band': qso.band or '',
                'mode': qso.mode or 'SSB',
                'frequency': qso.frequency,
                'rst_rcvd': qso.rst_rcvd or '',
                'rst_sent': qso.rst_sent or '',
                'my_gridsquare': qso.my_gridsquare or '',
                'gridsquare': qso.gridsquare or '',
                'sat_name': qso.sat_name or '',
                'prop_mode': qso.prop_mode or '',
                'cqz': qso.cqz,
                'ituz': qso.ituz,
                'lotw': qso.lotw or 'N',
            }
        })
    except (QSO.DoesNotExist, ValueError):
        return JsonResponse({'success': False, 'error': 'Запись не найдена'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def add_logbook_comment(request, callsign):
    """
    Добавление комментария к логу (logbook_search)
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не разрешён'}, status=405)

    try:
        import json
        data = json.loads(request.body)

        author_callsign = data.get('author_callsign', '').strip().upper()
        message = data.get('message', '').strip()
        captcha_answer = data.get('captcha_answer', '').strip()
        captcha_token = data.get('captcha_token', '').strip()

        if not author_callsign:
            return JsonResponse({'success': False, 'error': 'Введите позывной'}, status=400)

        if not message:
            return JsonResponse({'success': False, 'error': 'Введите сообщение'}, status=400)

        # Проверка капчи
        if not captcha_token or not captcha_answer:
            return JsonResponse({'success': False, 'error': 'Пройдите проверку капчи'}, status=400)

        # Проверяем токен капчи в сессии
        session_captcha = request.session.get('captcha_token', {})
        expected_answer = session_captcha.get(captcha_token, '')

        if str(captcha_answer) != str(expected_answer):
            return JsonResponse({'success': False, 'error': 'Неверный ответ на капчу'}, status=400)

        # Удаляем использованный токен
        if captcha_token in session_captcha:
            del session_captcha[captcha_token]
            request.session['captcha_token'] = session_captcha

        # Создаём комментарий, привязанный к конкретному позывному лога
        comment = LogbookComment.objects.create(
            callsign=callsign.upper(),
            author_callsign=author_callsign,
            message=message
        )

        return JsonResponse({
            'success': True,
            'message': 'Комментарий добавлен',
            'comment': {
                'id': str(comment.id),
                'callsign': comment.callsign,
                'author_callsign': comment.author_callsign,
                'message': comment.message,
                'created_at': comment.created_at.strftime('%d.%m.%Y %H:%M')
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def privacy(request):
    """
    Страница политики конфиденциальности
    """
    return render(request, 'privacy.html')