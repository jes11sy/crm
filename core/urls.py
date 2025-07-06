from rest_framework.routers import DefaultRouter
from .views import (
    GorodViewSet, TipZayavkiViewSet, RKViewSet, MasterViewSet, TipTranzakciiViewSet,
    TranzakciiViewSet, RoliViewSet, PolzovateliViewSet, PhoneGorodaViewSet, ZayavkiViewSet,
    MangoIncomingCallView, LoginView, LogoutView, ClearCookiesView, MeView, HealthCheckView, DetailedHealthCheckView, 
    MetricsView, PerformanceMetricsView, AlertHistoryView, SystemStatusView, ZayavkaFileViewSet, mango_audio_files,
    MangoEmailProcessingView, MasterPayoutViewSet, MasterFeedbackView
)
from .views.system import test_telegram_alert, trigger_test_error
from django.urls import path, include
from django.http import HttpResponseRedirect
from django_prometheus import exports

router = DefaultRouter()
router.register(r'gorod', GorodViewSet)
router.register(r'tipzayavki', TipZayavkiViewSet)
router.register(r'rk', RKViewSet)
router.register(r'master', MasterViewSet)
router.register(r'tiptranzakcii', TipTranzakciiViewSet)
router.register(r'tranzakcii', TranzakciiViewSet)
router.register(r'roli', RoliViewSet)
router.register(r'polzovateli', PolzovateliViewSet)
router.register(r'phonegoroda', PhoneGorodaViewSet)
router.register(r'zayavki', ZayavkiViewSet)
router.register(r'zayavka-files', ZayavkaFileViewSet)
router.register(r'master-payouts', MasterPayoutViewSet)

urlpatterns = [
    # Prometheus metrics
    path('metrics/', exports.ExportToDjangoView, name='prometheus-django-metrics'),
]

urlpatterns += router.urls + [
    path('mango-incoming-call/', MangoIncomingCallView.as_view(), name='mango_incoming_call'),
    path('mango-incoming-call/events/call/', MangoIncomingCallView.as_view(), name='mango_incoming_call_event_call'),
    path('mango-incoming-call/events/summary/', MangoIncomingCallView.as_view(), name='mango_incoming_call_event_summary'),
    path('mango-incoming-call/events/recording/', MangoIncomingCallView.as_view(), name='mango_incoming_call_event_recording'),
    path('mango-incoming-call/events/record/added/', MangoIncomingCallView.as_view(), name='mango_incoming_call_event_record_added'),
    path('vkhodyashchie-zayavki/', ZayavkiViewSet.as_view({'get': 'incoming'}), name='vkhodyashchie_zayavki'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('clear-cookies/', ClearCookiesView.as_view(), name='clear_cookies'),
    path('me/', MeView.as_view(), name='me'),
    
    # Health check endpoints
    path('health/', HealthCheckView.as_view(), name='health'),
    path('health/detailed/', DetailedHealthCheckView.as_view(), name='health_detailed'),
    path('metrics/', MetricsView.as_view(), name='metrics'),
    
    # Monitoring endpoints
    path('monitoring/performance/', PerformanceMetricsView.as_view(), name='performance_metrics'),
    path('monitoring/alerts/', AlertHistoryView.as_view(), name='alert_history'),
    path('monitoring/status/', SystemStatusView.as_view(), name='system_status'),
    
    # Mango Office audio files endpoint
    path('api/mango-audio-files/', mango_audio_files, name='mango_audio_files'),
    
    # Mango Office email processing endpoints
    path('mango/email-processing/', MangoEmailProcessingView.as_view(), name='mango_email_processing'),
    
    # Master Feedback endpoint
    path('master-feedback/', MasterFeedbackView.as_view()),
    
    # Telegram alerts testing endpoints
    path('test-telegram-alert/', test_telegram_alert, name='test_telegram_alert'),
    path('trigger-test-error/', trigger_test_error, name='trigger_test_error'),
] 