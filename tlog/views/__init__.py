"""
Пакет представлений (views)
"""
# Импорты из существующих модулей
from .auth import *
from .logbook import *
from .adif import *

# Импорты из основного модуля (для обратной совместимости)
from .main import *

# Прямые импорты из новых модулей для улучшения производительности
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
    delete_lotw_credentials,
    get_qso_details,
    lotw_filter_api,
    get_user_callsigns
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