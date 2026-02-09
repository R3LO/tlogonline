"""
Представления для logbook (для обратной совместимости)
Все функции перенесены в отдельные модули
"""

# Импорты из новых модулей для обратной совместимости
from .logbook_main import (
    logbook,
    logbook_search,
    clear_logbook,
)

from .qso import (
    add_qso,
    edit_qso,
    delete_qso,
    get_qso,
)

from .export import (
    export_adif,
)

from .privacy import (
    privacy,
)

from .qth_map import (
    qth_map,
)

from .achievements import (
    achievements,
    user_achievements,
)

from .helpers import (
    get_band_from_frequency,
    generate_adif_content,
)
