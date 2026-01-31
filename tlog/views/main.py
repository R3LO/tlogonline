# Main views - реэкспорт функций из отдельных модулей
# Этот файл обеспечивает обратную совместимость с существующими импортами

# Импортируем все функции из новых модулей
from .home import (
    home,
    get_callsigns_list,
    debug_callsigns,
    test_callsigns_simple,
    custom_404_view
)

from .profile import (
    profile_update,
    change_password
)

from .dashboard import (
    dashboard
)

from .chat import (
    chat_list,
    chat_send
)

from .lotw import (
    lotw_page,
    verify_lotw_credentials,
    delete_lotw_credentials
)

from .qo100 import (
    qo100_regions,
    qo100_r150s,
    qo100_grids,
    qo100_unique_callsigns,
    qo100_dxcc
)

from .qo100_converter import (
    qo100_converter,
    qo100_converter_download
)

from .cosmos import (
    cosmos_diploma,
    cosmos_download
)

from .api import (
    api_user_info,
    api_qso_stats,
    api_search_callsigns
)

# Экспортируем все функции для обратной совместимости
__all__ = [
    # Home functions
    'home',
    'get_callsigns_list', 
    'debug_callsigns',
    'test_callsigns_simple',
    'custom_404_view',
    
    # Profile functions
    'profile_update',
    'change_password',
    
    # Dashboard functions
    'dashboard',
    
    # Chat functions
    'chat_list',
    'chat_send',
    
    # LoTW functions
    'lotw_page',
    'verify_lotw_credentials',
    'delete_lotw_credentials',
    
    # QO-100 functions
    'qo100_regions',
    'qo100_r150s', 
    'qo100_grids',
    'qo100_unique_callsigns',
    'qo100_dxcc',
    'qo100_converter',
    'qo100_converter_download',
    
    # Cosmos functions
    'cosmos_diploma',
    'cosmos_download',
    
    # API functions
    'api_user_info',
    'api_qso_stats',
    'api_search_callsigns',
]