from django.db import models
from django.contrib.auth.models import User
import uuid


class ChatSession(models.Model):
    """Модель сессии чата для хранения истории переписки"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions', null=True, blank=True)
    session_name = models.CharField(max_length=255, default='Новый чат')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Сессия чата'
        verbose_name_plural = 'Сессии чатов'
    
    def __str__(self):
        return f"{self.session_name} ({self.user.username if self.user else 'Аноним'})"


class ChatMessage(models.Model):
    """Модель сообщения в чате"""
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('assistant', 'Ассистент'),
        ('system', 'Система'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
