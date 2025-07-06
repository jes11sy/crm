"""
Прокси-файл для импорта всех view-классов из папки views
"""
from .views import *

# Импортируем все views из модулей
from .views.base import (
    BaseViewSet, GorodViewSet, TipZayavkiViewSet, RKViewSet, PhoneGorodaViewSet
)
from .views.users import (
    MasterViewSet, RoliViewSet, PolzovateliViewSet, 
    LoginView, LogoutView, MeView, ClearCookiesView
)
from .views.zayavki import (
    ZayavkiViewSet, ZayavkaFileViewSet, 
    MangoIncomingCallView, MangoEmailProcessingView, mango_audio_files
)
from .views.finance import (
    TipTranzakciiViewSet, TranzakciiViewSet, MasterPayoutViewSet
)
from .views.system import (
    HealthCheckView, DetailedHealthCheckView, MetricsView, 
    PerformanceMetricsView, AlertHistoryView, SystemStatusView
)
from .views.feedback import MasterFeedbackView

# Экспортируем все views для обратной совместимости
__all__ = [
    'BaseViewSet',
    'GorodViewSet', 'TipZayavkiViewSet', 'RKViewSet', 'PhoneGorodaViewSet',
    'MasterViewSet', 'RoliViewSet', 'PolzovateliViewSet', 
    'LoginView', 'LogoutView', 'MeView', 'ClearCookiesView',
    'ZayavkiViewSet', 'ZayavkaFileViewSet', 
    'MangoIncomingCallView', 'MangoEmailProcessingView', 'mango_audio_files',
    'TipTranzakciiViewSet', 'TranzakciiViewSet', 'MasterPayoutViewSet',
    'HealthCheckView', 'DetailedHealthCheckView', 'MetricsView', 
    'PerformanceMetricsView', 'AlertHistoryView', 'SystemStatusView',
    'MasterFeedbackView',
]
