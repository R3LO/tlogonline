"""
URLs для фронтенда
"""
from django.urls import path, re_path
from .views import (
    home, register_page, login_page, dashboard, logbook,
    logout_view, adif_upload, clear_logbook,
    profile_update, logbook_search
)

urlpatterns = [
    # Веб-страницы
    path('', home, name='home'),
    path('register/', register_page, name='register_page'),
    path('debug-register/', register_page, name='debug_register'),
    path('login/', login_page, name='login_page'),
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/profile/', profile_update, name='profile_update'),
    path('dashboard/adif-upload/', adif_upload, name='adif_upload'),
    path('logbook/', logbook, name='logbook'),
    path('logbook/clear/', clear_logbook, name='clear_logbook'),
    path('logout/', logout_view, name='logout'),

    # Поиск по логам - динамический маршрут для позывных (должен быть последним)
    re_path(r'^(?P<callsign>[A-Za-z0-9/]+)/$', logbook_search, name='logbook_search'),
]