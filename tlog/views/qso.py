"""
Представления для работы с QSO (создание, редактирование, удаление)
"""
from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ..models import QSO, check_user_blocked
@login_required
def edit_qso(request, qso_id):
    """
    Редактирование одной записи QSO
    """
    # Проверяем, не заблокирован ли пользователь
    is_blocked, reason = check_user_blocked(request.user)
    if is_blocked:
        return JsonResponse({'success': False, 'error': 'Ваш аккаунт заблокирован'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не разрешён'}, status=405)

    try:
        qso = QSO.objects.get(id=qso_id, user=request.user)
    except (QSO.DoesNotExist, ValueError):
        return JsonResponse({'success': False, 'error': 'Запись не найдена'}, status=404)

    try:
        import json
        from .. import r150s
        from ..region_ru import RussianRegionFinder
        import os
        from django.conf import settings
        from django.db.models import Q

        data = json.loads(request.body)

        # Обновляем поля записи (все текстовые поля преобразуются в верхний регистр)
        qso.date = data.get('date')
        qso.time = data.get('time')
        qso.my_callsign = data.get('my_callsign', '').upper()[:20]
        qso.callsign = data.get('callsign', '').upper()[:20]
        qso.band = data.get('band', '').upper()[:10] or None
        qso.mode = (data.get('mode') or 'SSB').upper()

        frequency = data.get('frequency')
        if frequency:
            try:
                qso.frequency = float(frequency)
            except (ValueError, TypeError):
                qso.frequency = None
        else:
            qso.frequency = None

        qso.rst_rcvd = data.get('rst_rcvd', '').upper()[:10] or None
        qso.rst_sent = data.get('rst_sent', '').upper()[:10] or None
        qso.my_gridsquare = data.get('my_gridsquare', '').upper()[:10] or None
        qso.gridsquare = data.get('gridsquare', '').upper()[:10] or None
        qso.sat_name = data.get('sat_name', '').upper()[:50] or None
        qso.prop_mode = data.get('prop_mode', '').upper()[:50] or None

        qso.paper_qsl = data.get('paper_qsl', 'N')

        # Получаем callsign для пересчёта
        callsign = qso.callsign

        # Если lotw = N, принимаем cqz, ituz, continent, r150s, dxcc, state из формы
        # Если lotw = Y, оставляем их без изменений (они заблокированы на клиенте)
        if qso.lotw != 'Y':
            # Сохраняем как есть - пустые значения будут None
            cqz_val = data.get('cqz')
            ituz_val = data.get('ituz')
            qso.cqz = int(cqz_val) if cqz_val and str(cqz_val).strip() else None
            qso.ituz = int(ituz_val) if ituz_val and str(ituz_val).strip() else None
            qso.continent = (data.get('continent') or '').upper()[:10] or None
            qso.r150s = (data.get('r150s') or '').upper()[:100] or None
            qso.dxcc = (data.get('dxcc') or '').upper()[:10] or None
            qso.state = (data.get('state') or '').upper()[:10] or None
        else:
            # lotw = Y - поля заблокированы на клиенте, оставляем как есть
            pass

        # Пересчитываем cqz, ituz, continent, r150s, dxcc, state по позывному ТОЛЬКО если они пустые в форме
        # и lotw != 'Y'
        if qso.lotw != 'Y' and callsign and not data.get('cqz') and not data.get('ituz'):
            # Инициализируем базы данных CTY и R150
            tlog_dir = os.path.join(settings.BASE_DIR, 'tlog')
            db_path = os.path.join(tlog_dir, 'r150cty.dat')
            cty_path = os.path.join(tlog_dir, 'cty.dat')

            r150s.init_database(db_path)
            r150s.init_cty_database(cty_path)

            dxcc_info = r150s.get_dxcc_info(callsign, db_path)
            if dxcc_info:
                # Заполняем cqz, ituz и continent если не указаны в форме
                if not data.get('cqz'):
                    qso.cqz = dxcc_info.get('cq_zone')
                if not data.get('ituz'):
                    qso.ituz = dxcc_info.get('itu_zone')
                if not data.get('continent'):
                    qso.continent = dxcc_info.get('continent')
                if not data.get('r150s'):
                    r150s_country = dxcc_info.get('country')
                    qso.r150s = r150s_country.upper()[:100] if r150s_country else None
                if not data.get('dxcc'):
                    dxcc = r150s.get_cty_primary_prefix(callsign, cty_path)
                    qso.dxcc = dxcc.upper()[:10] if dxcc else None

                # Определяем код региона России только для российских позывных (UA, UA9, UA2)
                if qso.dxcc and qso.dxcc.upper() in ('UA', 'UA9', 'UA2') and not data.get('state'):
                    exceptions_path = os.path.join(settings.BASE_DIR, 'tlog', 'exceptions.dat')
                    region_finder = RussianRegionFinder(exceptions_file=exceptions_path)
                    qso.state = region_finder.get_region_code(callsign)
                elif not data.get('state'):
                    qso.state = None

        qso.save()

        return JsonResponse({'success': True, 'message': 'Запись успешно обновлена'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


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
                'continent': qso.continent or '',
                'r150s': qso.r150s or '',
                'dxcc': qso.dxcc or '',
                'state': qso.state or '',
                'paper_qsl': qso.paper_qsl or 'N',
            }
        })
    except (QSO.DoesNotExist, ValueError):
        return JsonResponse({'success': False, 'error': 'Запись не найдена'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



@login_required
def add_qso(request):
    """
    Добавление новой записи QSO
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    # Проверяем, не заблокирован ли пользователь
    is_blocked, reason = check_user_blocked(request.user)
    if is_blocked:
        return JsonResponse({'error': 'Ваш аккаунт заблокирован'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        import json
        from .. import r150s
        from ..region_ru import RussianRegionFinder
        import os
        from django.conf import settings
        from django.db.models import Q

        data = json.loads(request.body)

        # Получаем данные из формы (все текстовые поля преобразуются в верхний регистр)
        date_str = data.get('date')
        time_str = data.get('time')
        my_callsign = data.get('my_callsign', '').strip().upper()[:20] or request.user.username.upper()
        callsign = data.get('callsign', '').strip().upper()[:20]
        band = data.get('band', '').strip().upper()[:10] or None
        mode = (data.get('mode') or 'SSB').upper()

        # Проверка на дубликат (мой позывной, позывной корреспондента, дата, время - только часы и минуты, вид связи, диапазон)
        # Нормализуем данные для сравнения
        my_callsign_normalized = my_callsign.upper()
        callsign_normalized = callsign.upper()
        my_callsign_normalized = my_callsign.upper() if my_callsign else ''
        callsign_normalized = callsign.upper() if callsign else ''
        mode_normalized = mode.upper() if mode else 'SSB'
        band_normalized = band.upper() if band else None

        # Получаем время из запроса (формат HH:MM или HH:MM:SS)
        time_parts = time_str.split(':')
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0

        # Создаем базовый запрос - сравниваем только часы и минуты (без секунд)
        duplicate_query = Q(
            user=request.user,
            my_callsign__iexact=my_callsign_normalized,
            callsign__iexact=callsign_normalized,
            date=date_str,
            mode__iexact=mode_normalized,
            time__hour=hour,
            time__minute=minute
        )

        # Добавляем диапазон если он указан
        if band_normalized:
            duplicate_query &= Q(band__iexact=band_normalized)
        else:
            duplicate_query &= Q(band__isnull=True) | Q(band='')

        duplicate_exists = QSO.objects.filter(duplicate_query).exists()

        if duplicate_exists:
            return JsonResponse({
                'error': f'QSO с {callsign_normalized} на {date_str} {hour:02d}:{minute:02d} {mode_normalized}/{band_normalized or "не указан"} уже существует'
            }, status=400)

        # Проверяем обязательные поля
        if not all([date_str, time_str, callsign, band]):
            return JsonResponse({
                'error': 'Заполните обязательные поля: дата, время, позывной, диапазон'
            }, status=400)

        # Валидация форматов
        if len(callsign) > 20:
            return JsonResponse({
                'error': 'Позывной не должен превышать 20 символов'
            }, status=400)

        frequency = data.get('frequency')
        rst_rcvd = data.get('rst_rcvd', '').upper()[:10] or None
        rst_sent = data.get('rst_sent', '').upper()[:10] or None
        my_gridsquare = data.get('my_gridsquare', '').upper()[:10] or None
        gridsquare = data.get('gridsquare', '').upper()[:10] or None
        sat_qso = data.get('sat_qso', 'N')
        prop_mode = data.get('prop_mode', '').upper()[:50] or None
        sat_name = data.get('sat_name', '').upper()[:50] or None
        lotw = data.get('lotw', 'N')
        paper_qsl = data.get('paper_qsl', 'N')

        # Инициализируем базы данных CTY и R150
        tlog_dir = os.path.join(settings.BASE_DIR, 'tlog')
        db_path = os.path.join(tlog_dir, 'r150cty.dat')
        cty_path = os.path.join(tlog_dir, 'cty.dat')

        r150s.init_database(db_path)
        r150s.init_cty_database(cty_path)

        # Поля SAT - только если Sat QSO отмечен
        if sat_qso == 'Y':
            sat_name = data.get('sat_name', '').upper()[:50] or None
            sat_prop_mode = data.get('prop_mode', '').upper()[:50] or None
            prop_mode = sat_prop_mode
        else:
            sat_name = None
            prop_mode = None

        # Если cqz и ituz не переданы из формы, получаем из баз данных CTY
        cqz = data.get('cqz')
        ituz = data.get('ituz')
        continent = None

        # Получаем информацию о позывном из баз данных
        if callsign:
            dxcc_info = r150s.get_dxcc_info(callsign, db_path)
            if dxcc_info:
                # Заполняем cqz, ituz и continent если не указаны в форме
                if not cqz:
                    cqz = dxcc_info.get('cq_zone')
                if not ituz:
                    ituz = dxcc_info.get('itu_zone')
                if not continent:
                    continent = dxcc_info.get('continent')

                # Получаем country из r150cty.dat (преобразуем в верхний регистр)
                r150s_country = dxcc_info.get('country')
                if r150s_country:
                    r150s_country = r150s_country.upper()[:100]

                # Получаем dxcc (primary_prefix) из cty.dat
                dxcc = r150s.get_cty_primary_prefix(callsign, cty_path)
                if dxcc:
                    dxcc = dxcc.upper()[:10]
            else:
                r150s_country = None
                dxcc = None
        else:
            r150s_country = None
            dxcc = None

        # Определяем код региона России только для российских позывных (UA, UA9, UA2)
        state = None
        if callsign and dxcc:
            if dxcc.upper() in ('UA', 'UA9', 'UA2') and not data.get('state'):
                exceptions_path = os.path.join(settings.BASE_DIR, 'tlog', 'exceptions.dat')
                region_finder = RussianRegionFinder(exceptions_file=exceptions_path)
                state = region_finder.get_region_code(callsign)
            elif not data.get('state'):
                state = None

        # Создаем QSO
        qso = QSO.objects.create(
            user=request.user,
            my_callsign=my_callsign,
            callsign=callsign,
            date=date_str,
            time=time_str,
            band=band,
            mode=mode,
            frequency=float(frequency) if frequency else None,
            rst_rcvd=rst_rcvd,
            rst_sent=rst_sent,
            my_gridsquare=my_gridsquare,
            gridsquare=gridsquare,
            sat_name=sat_name,
            prop_mode=prop_mode,
            cqz=int(cqz) if cqz else None,
            ituz=int(ituz) if ituz else None,
            lotw=lotw,
            paper_qsl=paper_qsl,
            r150s=r150s_country if r150s_country else None,
            dxcc=dxcc if dxcc else None,
            continent=continent if continent else None,
            state=state
        )

        return JsonResponse({
            'success': True,
            'message': 'QSO успешно добавлено',
            'qso_id': str(qso.id)
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


