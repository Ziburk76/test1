"""URL маршруты приложения chatbot."""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='chat_index'),
    path('tests/', views.tests_page, name='tests_page'),
    path('api/chat/', views.chat, name='api_chat'),
    path('api/check/', views.check_connection, name='api_check'),
    path('api/session/', views.session_info, name='api_session'),
    path('api/reset/', views.reset_session, name='api_reset'),
    path('api/compare/', views.compare_sql, name='api_compare'),
    path('api/debug/schema/', views.debug_schema, name='api_debug_schema'),
]
