"""
URLs для фронтенда
"""
from django.urls import path, re_path
from django.views.generic import RedirectView
from .views import (
    home, register_page, login_page, dashboard, logbook,
    logout_view, adif_upload, clear_logbook,
    profile_update, logbook_search, delete_adif_uploads,
    edit_qso, delete_qso, get_qso,
    privacy, export_adif, qth_map, achievements, add_qso,
    get_callsigns_list, chat_list, chat_send,
    verify_lotw_credentials, delete_lotw_credentials,
    change_password, user_achievements,
    qo100_regions, qo100_r150s, qo100_grids, qo100_unique_callsigns,
    qo100_dxcc, qo100_converter, qo100_converter_download,
    cosmos_diploma, cosmos_download,
    lotw_page, debug_callsigns, test_callsigns_simple, lotw_filter_api, get_user_callsigns, get_qso_details
)

urlpatterns = [
    path('', home, name='home'),
    path('register/', register_page, name='register_page'),
    path('debug-register/', register_page, name='debug_register'),
    path('login/', login_page, name='login_page'),
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/profile/', profile_update, name='profile_update'),
    path('dashboard/debug-callsigns/', debug_callsigns, name='debug_callsigns'),
    path('dashboard/test-callsigns/', test_callsigns_simple, name='test_callsigns_simple'),
    path('dashboard/profile/verify-lotw/', verify_lotw_credentials, name='verify_lotw_credentials'),
    path('dashboard/profile/delete-lotw/', delete_lotw_credentials, name='delete_lotw_credentials'),
    path('api/lotw/filter/', lotw_filter_api, name='lotw_filter_api'),
    path('api/lotw/callsigns/', get_user_callsigns, name='get_user_callsigns'),
    path('api/lotw/qso-details/', get_qso_details, name='get_qso_details'),
    path('dashboard/profile/change-password/', change_password, name='change_password'),
    path('lotw/', lotw_page, name='lotw_page'),
    path('dashboard/adif-upload/', adif_upload, name='adif_upload'),
    path('dashboard/adif-delete/<uuid:upload_id>/', delete_adif_uploads, name='delete_adif_uploads'),
    path('dashboard/chat/list/', chat_list, name='chat_list'),
    path('dashboard/chat/send/', chat_send, name='chat_send'),
    # QO-100 рейтинги
    path('dashboard/qo100/regions/', qo100_regions, name='qo100_regions'),
    path('dashboard/qo100/r150s/', qo100_r150s, name='qo100_r150s'),
    path('dashboard/qo100/dxcc/', qo100_dxcc, name='qo100_dxcc'),
    path('dashboard/qo100/grids/', qo100_grids, name='qo100_grids'),
    path('dashboard/qo100/unique-callsigns/', qo100_unique_callsigns, name='qo100_unique_callsigns'),
    path('dashboard/qo100/dxcc/', qo100_dxcc, name='qo100_dxcc'),
    # QO-100 конвертер
    path('dashboard/qo100/converter/', qo100_converter, name='qo100_converter'),
    path('dashboard/qo100/converter/download/', qo100_converter_download, name='qo100_converter_download'),
    # Диплом Космос
    path('dashboard/cosmos/', cosmos_diploma, name='cosmos_diploma'),
    path('dashboard/cosmos/download/', cosmos_download, name='cosmos_download'),
    path('logbook/', logbook, name='logbook'),
    path('logbook/add/', add_qso, name='add_qso'),
    path('logbook/clear/', clear_logbook, name='clear_logbook'),
    path('logbook/export/', export_adif, name='export_adif'),
    path('logbook/edit/<uuid:qso_id>/', edit_qso, name='edit_qso'),
    path('logbook/delete/<uuid:qso_id>/', delete_qso, name='delete_qso'),
    path('logbook/get/<uuid:qso_id>/', get_qso, name='get_qso'),
    path('logout/', logout_view, name='logout'),
    path('privacy/', privacy, name='privacy'),
    path('search-callsigns/', get_callsigns_list, name='get_callsigns_list'),
    path('qth-map/', qth_map, name='qth_map'),
    path('qth-loc.html', RedirectView.as_view(url='/static/qth-loc.html', permanent=False), name='qth_loc'),
    path('achievements/', achievements, name='achievements'),
    path('user-awards/', user_achievements, name='user_achievements'),
    re_path(r'^(?P<callsign>[A-Za-z0-9/]+)/$', logbook_search, name='logbook_search'),
]