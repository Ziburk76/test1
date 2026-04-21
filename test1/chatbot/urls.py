"""URL маршруты приложения chatbot."""
from django.urls import path
from . import views

urlpatterns = [
    # Страницы авторизации
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Чат
    path('', views.chat, name='chat'),
    path('tests/', views.tests_page, name='tests_page'),
    
    # API для создания сессии
    path('session/create/', views.create_session, name='create_session'),
    path('session/<uuid:session_id>/delete/', views.delete_session, name='delete_session'),
    path('session/<uuid:session_id>/history/', views.load_session_history, name='load_session_history'),
    
    # API чата и проверок
    path('api/chat/', views.chat_api, name='api_chat'),
    path('api/check/', views.check_connection, name='api_check'),
    path('api/session/', views.session_info, name='api_session'),
    path('api/reset/', views.reset_session, name='api_reset'),
    path('api/compare/', views.compare_sql, name='api_compare'),
    path('api/debug/schema/', views.debug_schema, name='api_debug_schema'),
]
