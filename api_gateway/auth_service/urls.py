from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'auth_service'

urlpatterns = [
    # Аутентификация
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Профиль пользователя
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # Сессии и попытки входа
    path('sessions/', views.UserSessionsView.as_view(), name='sessions'),
    path('login-attempts/', views.LoginAttemptsView.as_view(), name='login_attempts'),
    
    # Health check
    path('health/', views.health_check, name='health'),
] 