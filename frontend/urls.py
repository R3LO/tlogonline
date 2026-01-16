"""
URLs для фронтенда
"""
from django.urls import path
from .views import (
    home, register_page, login_page, dashboard, logbook,
    register_api, login_api, logout_view, adif_upload, clear_logbook,
    profile_update
)

urlpatterns = [
    # Веб-страницы
    path('', home, name='home'),
    path('register/', register_page, name='register_page'),
    path('debug-register/', register_page, name='debug_register'),  # Временно для отладки
    path('login/', login_page, name='login_page'),
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/profile/', profile_update, name='profile_update'),
    path('dashboard/adif-upload/', adif_upload, name='adif_upload'),
    path('logbook/', logbook, name='logbook'),  # Добавлен маршрут для logbook
    path('logbook/clear/', clear_logbook, name='clear_logbook'),
    path('logout/', logout_view, name='logout'),

    # API для веб-интерфейса
    path('api/web/register/', register_api, name='register_api'),
    path('api/web/login/', login_api, name='login_api'),
]