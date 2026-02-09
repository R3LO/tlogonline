"""
Пакет представлений (views)
"""
# Импорты из существующих модулей
from .auth import *
from .adif import *

# Импорты из основного модуля (для обратной совместимости)
from .main import *

# Импорты из logbook модулей (новая структура)
from .logbook_main import (
    logbook,
    logbook_search,
    clear_logbook
)

from .qso import (
    add_qso,
    edit_qso,
    delete_qso,
    get_qso
)

from .export import (
    export_adif
)

from .privacy import (
    privacy
)

from .qth_map import (
    qth_map
)

from .achievements import (
    achievements,
    user_achievements
)

from .helpers import (
    get_band_from_frequency,
    generate_adif_content
)

# Прямые импорты из других модулей для улучшения производительности
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
    get_user_callsigns,
    lotw_regions_api,
    export_lotw_adif
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
    api_search_callsigns,
    api_cosmos_user_data,
    api_cosmos_generate,
    api_cosmos_download
)