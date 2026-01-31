# Функции чата

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ..models import ChatMessage, RadioProfile


@login_required
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
            'created_at': msg.created_at.strftime('%d.%m.%Y %H:%M'),
        })

    return JsonResponse({'messages': messages_data})


@login_required
def chat_send(request):
    """
    Отправка нового сообщения в чат
    """
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
                'created_at': chat_message.created_at.strftime('%d.%m.%Y %H:%M'),
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)