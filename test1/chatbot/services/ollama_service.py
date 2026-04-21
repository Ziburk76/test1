"""
Сервис для взаимодействия с Ollama API.
"""
import requests
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class OllamaService:
    """Сервис для отправки запросов к локальной модели Ollama."""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.api_url = f"{self.base_url}/api/chat"
        self.generate_url = f"{self.base_url}/api/generate"

    def chat(self, messages, temperature=0.2, stream=False):
        """
        Отправить сообщение в чат-модель.
        
        Args:
            messages: список словарей с ролями ('system', 'user', 'assistant')
            temperature: креативность ответа (0.2 - детерминированно)
            stream: потоковая отдача
        
        Returns:
            str: текст ответа модели
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
            "options": {
                "num_ctx": 8192,
            }
        }

        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            return result.get('message', {}).get('content', '')
        except requests.exceptions.ConnectionError:
            logger.error("Не удалось подключиться к Ollama. Проверьте, запущен ли Ollama.")
            return "Ошибка: не удалось подключиться к Ollama. Убедитесь, что Ollama запущен (команда: ollama serve)."
        except requests.exceptions.Timeout:
            logger.error("Таймаут запроса к Ollama.")
            return "Ошибка: превышено время ожидания ответа от модели. Попробуйте ещё раз."
        except Exception as e:
            logger.error(f"Ошибка при запросе к Ollama: {e}")
            return f"Ошибка при обработке запроса: {str(e)}"

    def generate(self, prompt, system_prompt=None, temperature=0.2):
        """
        Сгенерировать ответ в режиме completion.
        
        Args:
            prompt: текст запроса
            system_prompt: системная инструкция
            temperature: креативность
        
        Returns:
            str: текст ответа
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": False,
            "options": {
                "num_ctx": 8192,
            }
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(
                self.generate_url,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            return result.get('response', '')
        except Exception as e:
            logger.error(f"Ошибка при генерации: {e}")
            return f"Ошибка: {str(e)}"

    def check_connection(self):
        """Проверить доступность Ollama."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False


# Singleton
ollama_service = OllamaService()
