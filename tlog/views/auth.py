"""
Представления для аутентификации (регистрация, вход, выход)
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from ..models import RadioProfile


def register_page(request):
    """
    Страница регистрации
    """
    if request.method == 'POST':
        # Действующий позывной используется как логин
        callsign = request.POST.get('callsign', '').strip().upper()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        qth = request.POST.get('qth', '').strip()
        qth_locator = request.POST.get('qth_locator', '').strip().upper()

        # Валидация
        if not all([callsign, email, password, password_confirm]):
            messages.error(request, 'Все обязательные поля должны быть заполнены')
            return render(request, 'register_base.html')

        if password != password_confirm:
            messages.error(request, 'Пароли не совпадают')
            return render(request, 'register_base.html')

        if len(password) < 8:
            messages.error(request, 'Пароль должен содержать минимум 8 символов')
            return render(request, 'register_base.html')

        # Проверяем уникальность позывного (как username)
        if User.objects.filter(username=callsign).exists():
            messages.error(request, 'Пользователь с таким позывным уже существует')
            return render(request, 'register_base.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже существует')
            return render(request, 'register_base.html')

        # Создаем пользователя (позывной = username)
        try:
            from ..models import RadioProfile

            user = User.objects.create_user(
                username=callsign,
                email=email,
                password=password
            )

            # Создаем профиль радиолюбителя
            RadioProfile.objects.create(
                user=user,
                callsign=callsign,
                first_name=first_name,
                last_name=last_name,
                qth=qth,
                my_gridsquare=qth_locator
            )

            messages.success(request, 'Регистрация успешна! Теперь вы можете войти.')
            return redirect('login_page')

        except Exception as e:
            messages.error(request, f'Ошибка при регистрации: {str(e)}')
            return render(request, 'register_base.html')

    return render(request, 'register_base.html')


def login_page(request):
    """
    Страница входа
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip().upper()
        password = request.POST.get('password')
        remember_me = request.POST.get('rememberMe')

        # Проверяем обязательные поля
        if not username or not password:
            messages.error(request, _('Имя пользователя и пароль обязательны'))
            return render(request, 'login_base.html')

        # Аутентификация
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Проверяем, не заблокирован ли пользователь
            try:
                profile = user.radio_profile
                if profile.is_blocked:
                    messages.error(request, _('Ваш аккаунт заблокирован. Причина: ') + (profile.blocked_reason or ''))
                    return render(request, 'login_base.html')
            except RadioProfile.DoesNotExist:
                pass  # Профиля нет - считаем пользователя незаблокированным

            login(request, user)

            # Если отмечен "Запомнить меня", сохраняем данные в cookies
            if remember_me:
                response = redirect('dashboard')
                response.set_cookie('remembered_username', username, 30*24*60*60)
                response.set_cookie('remembered_password', password, 30*24*60*60)
                return response
            else:
                response = redirect('dashboard')
                response.delete_cookie('remembered_username')
                response.delete_cookie('remembered_password')
                return response
        else:
            messages.error(request, _('Неверные учетные данные'))
            return render(request, 'login_base.html')

    return render(request, 'login_base.html')


def logout_view(request):
    """
    Выход пользователя
    """
    logout(request)
    return redirect('home')