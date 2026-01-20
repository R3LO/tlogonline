"""
URLs для фронтенда
"""
from django.urls import path, re_path
from .views import (
    home, register_page, login_page, dashboard, logbook,
    logout_view, adif_upload, clear_logbook,
    profile_update, logbook_search, delete_adif_uploads,
    edit_qso, delete_qso, get_qso,
    privacy, export_adif, qth_map, achievements, add_qso
)

urlpatterns = [
    path('', home, name='home'),
    path('register/', register_page, name='register_page'),
    path('debug-register/', register_page, name='debug_register'),
    path('login/', login_page, name='login_page'),
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/profile/', profile_update, name='profile_update'),
    path('dashboard/adif-upload/', adif_upload, name='adif_upload'),
    path('dashboard/adif-delete/<uuid:upload_id>/', delete_adif_uploads, name='delete_adif_uploads'),
    path('logbook/', logbook, name='logbook'),
    path('logbook/add/', add_qso, name='add_qso'),
    path('logbook/clear/', clear_logbook, name='clear_logbook'),
    path('logbook/export/', export_adif, name='export_adif'),
    path('logbook/edit/<uuid:qso_id>/', edit_qso, name='edit_qso'),
    path('logbook/delete/<uuid:qso_id>/', delete_qso, name='delete_qso'),
    path('logbook/get/<uuid:qso_id>/', get_qso, name='get_qso'),
    path('logout/', logout_view, name='logout'),
    path('privacy/', privacy, name='privacy'),
    path('qth-map/', qth_map, name='qth_map'),
    path('achievements/', achievements, name='achievements'),
    re_path(r'^(?P<callsign>[A-Za-z0-9/]+)/$', logbook_search, name='logbook_search'),
]