"""
Модели CRM системы
"""

# Импортируем все модели для обратной совместимости
from .base import Gorod, TipZayavki
from .users import Roli, Polzovateli, Master
from .business import RK, PhoneGoroda
from .finance import TipTranzakcii, Tranzakcii, MasterPayout
from .requests import Zayavki, ZayavkaFile

# Экспортируем все модели
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