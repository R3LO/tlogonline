"""
Middleware для обработки языка из куки
"""
from django.utils import translation
from django.conf import settings


class LanguageMiddleware:
    """
    Middleware для сохранения языка в куках и восстановления из них
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Проверяем, есть ли язык в куках
        language_code = request.COOKIES.get('django_language')
        
        # Если язык в куках и он в списке доступных языков, устанавливаем его
        if language_code:
            available_languages = dict(settings.LANGUAGES)
            if language_code in available_languages:
                translation.activate(language_code)
                request.LANGUAGE_CODE = language_code

        response = self.get_response(request)

        # Если язык был активирован, сохраняем его в куку
        if hasattr(request, 'LANGUAGE_CODE'):
            language_code = request.LANGUAGE_CODE
            # Сохраняем язык на 1 год (365 дней)
            response.set_cookie(
                'django_language',
                language_code,
                max_age=365 * 24 * 60 * 60,
                httponly=False,
                samesite='Lax'
            )

        return response
