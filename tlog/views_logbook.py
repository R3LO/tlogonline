"""
Представление для страницы лога радиосвязей (logbook)
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import QSO


@login_required
def logbook(request):
    """
    Страница лога радиосвязей
    """
    # Получаем QSO пользователя
    user_qso = QSO.objects.filter(user=request.user).order_by('-date', '-time')

    # Подсчитываем статистику
    total_qso = user_qso.count()

    # Статистика по видам модуляции
    mode_stats = {}
    mode_choices = dict(QSO._meta.get_field('mode').choices)
    for mode in mode_choices.keys():
        count = user_qso.filter(mode=mode).count()
        if count > 0:
            mode_stats[mode] = count

    # Статистика по диапазонам
    band_stats = {}
    bands = [
        ('160m', 1.8, 2.0),
        ('80m', 3.5, 4.0),
        ('40m', 7.0, 7.3),
        ('20m', 14.0, 14.35),
        ('15m', 21.0, 21.45),
        ('10m', 28.0, 29.7),
        ('6m', 50.0, 54.0),
        ('2m', 144.0, 148.0),
        ('70cm', 420.0, 450.0),
    ]

    for band_name, min_freq, max_freq in bands:
        count = user_qso.filter(frequency__gte=min_freq, frequency__lte=max_freq).count()
        if count > 0:
            band_stats[band_name] = count

    context = {
        'user_qso': user_qso,
        'total_qso': total_qso,
        'mode_statistics': mode_stats,
        'band_statistics': band_stats,
    }

    return render(request, 'logbook.html', context)


@login_required
@require_http_methods(["POST"])
def clear_logbook(request):
    """
    Очистка всего лога радиосвязей
    """
    try:
        # Удаляем все QSO пользователя
        deleted_count = QSO.objects.filter(user=request.user).delete()[0]

        if deleted_count > 0:
            messages.success(request, f'Лог очищен. Удалено {deleted_count} записей QSO.')
        else:
            messages.info(request, 'Лог уже пуст.')

        return JsonResponse({
            'success': True,
            'message': f'Лог очищен. Удалено {deleted_count} записей.',
            'deleted_count': deleted_count
        })

    except Exception as e:
        messages.error(request, f'Ошибка при очистке лога: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)