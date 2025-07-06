"""
Модели CRM системы - основной файл для обратной совместимости
"""

# Импортируем все модели из модулей
from .models.base import Gorod, TipZayavki
from .models.users import Roli, Polzovateli, Master
from .models.business import RK, PhoneGoroda
from .models.finance import TipTranzakcii, Tranzakcii, MasterPayout
from .models.requests import Zayavki, ZayavkaFile

# Экспортируем все модели для обратной совместимости
__all__ = [
    'Gorod',
    'TipZayavki', 
    'RK',
    'Master',
    'TipTranzakcii',
    'Tranzakcii',
    'Roli',
    'Polzovateli',
    'PhoneGoroda',
    'Zayavki',
    'ZayavkaFile',
    'MasterPayout',
] 