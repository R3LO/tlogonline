"""
Главный файл представлений - импортирует функции из модулей
"""
# Импорты из модуля аутентификации
from .views.auth import (
    register_page,
    login_page,
    logout_view,
)

# Импорты из модуля основных страниц
from .views.main import (
    home,
    dashboard,
    profile_update,
    lotw_page,
)

# Импорты из модуля логбука
from .views.logbook import (
    get_band_from_frequency,
    logbook,
    logbook_search,
    clear_logbook,
)

# Импорты из модуля ADIF
from .views.adif import (
    adif_upload,
    process_adif_file,
    parse_adif_record,
    delete_adif_uploads,
)