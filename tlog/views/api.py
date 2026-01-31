# API функции

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


@login_required
def api_user_info(request):
    """
    API для получения информации о пользователе
    """
    try:
        from ..models import RadioProfile, QSO
        
        # Базовая информация о пользователе
        user_info = {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'date_joined': request.user.date_joined.isoformat(),
        }
        
        # Информация из профиля радиолюбителя
        try:
            profile = request.user.radio_profile
            user_info.update({
                'callsign': profile.callsign,
                'qth': profile.qth,
                'my_gridsquare': profile.my_gridsquare,
                'lotw_user': profile.lotw_user,
                'lotw_chk_pass': profile.lotw_chk_pass,
            })
        except RadioProfile.DoesNotExist:
            user_info['callsign'] = request.user.username
        
        # Статистика QSO
        user_qso = QSO.objects.filter(user=request.user)
        user_info['qso_stats'] = {
            'total_qso': user_qso.count(),
            'unique_callsigns': user_qso.values('callsign').distinct().count(),
            'dxcc_count': user_qso.exclude(dxcc__isnull=True).exclude(dxcc='').values('dxcc').distinct().count(),
        }
        
        return JsonResponse({
            'success': True,
            'user_info': user_info
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def api_qso_stats(request):
    """
    API для получения статистики QSO пользователя
    """
    try:
        from ..models import QSO
        from collections import Counter
        
        user_qso = QSO.objects.filter(user=request.user)
        
        # Общая статистика
        total_qso = user_qso.count()
        unique_callsigns = user_qso.values('callsign').distinct().count()
        
        # Статистика по диапазонам
        bands = user_qso.values_list('band', flat=True)
        band_stats = dict(Counter(bands))
        
        # Статистика по модуляции
        modes = user_qso.values_list('mode', flat=True)
        mode_stats = dict(Counter(modes))
        
        # Статистика по годам
        years = [qso.date.year for qso in user_qso]
        year_stats = dict(Counter(years))
        
        # Последние QSO
        recent_qso = user_qso.order_by('-date', '-time')[:10].values(
            'callsign', 'date', 'time', 'band', 'mode', 'gridsquare'
        )
        
        return JsonResponse({
            'success': True,
            'stats': {
                'total_qso': total_qso,
                'unique_callsigns': unique_callsigns,
                'band_statistics': band_stats,
                'mode_statistics': mode_stats,
                'year_statistics': year_stats,
                'recent_qso': list(recent_qso),
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def api_search_callsigns(request):
    """
    API для поиска позывных (аналог get_callsigns_list)
    """
    query = request.GET.get('q', '').upper()
    limit = int(request.GET.get('limit', 10))
    
    if len(query) < 1:
        return JsonResponse({'callsigns': []})
    
    try:
        from ..models import QSO, RadioProfile
        import json
        
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
        
        # Ограничиваем и сортируем
        callsigns_list = sorted(list(callsigns_set))[:limit]
        
        return JsonResponse({
            'success': True,
            'callsigns': callsigns_list
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)