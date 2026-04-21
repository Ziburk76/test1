"""
Сервис для генерации понятного ответа на основе SQL-результатов.
"""
import json
import logging
from .ollama_service import ollama_service

logger = logging.getLogger(__name__)

ANSWER_SYSTEM_PROMPT = """Ты — помощник-аналитик производственной базы данных завода.
Твоя задача: объяснить пользователю результаты SQL-запроса понятным русским языком.

Правила:
1. Отвечай на русском языке.
2. Будь конкретен — приводи числа, имена, даты из результатов.
3. Если результатов нет (пусто), скажи: "По вашему запросу данных не найдено."
4. Если результатов много, обобщи ключевые цифры.
5. Используй таблицы в markdown-формате для наглядности.
6. Будь краток, но информативен.
7. Если есть аномалии (нулевые значения, большие потери) — обрати внимание.
"""


class AnswerGenerator:
    """Генерирует понятный ответ на основе SQL-результатов."""

    def generate(self, question: str, sql: str, db_result: dict) -> str:
        """
        Сгенерировать ответ для пользователя.
        
        Args:
            question: исходный вопрос пользователя
            sql: выполненный SQL-запрос
            db_result: результат выполнения запроса (dict от db_executor)
        
        Returns:
            str: текст ответа
        """
        if not db_result.get('success'):
            return f"❌ {db_result.get('error', 'Произошла ошибка при выполнении запроса.')}"

        rows = db_result.get('rows', [])
        count = db_result.get('count', 0)

        if count == 0:
            return "📭 По вашему запросу данных не найдено. Попробуйте переформулировать вопрос или уточните параметры."

        # Формируем краткое описание результатов для контекста
        result_summary = json.dumps({
            'columns': db_result.get('columns', []),
            'row_count': count,
            'sample_rows': rows[:10],  # Первые 10 для контекста
        }, ensure_ascii=False, default=str)

        user_message = f"""Вопрос пользователя: {question}

SQL-запрос: {sql}

Результаты ({count} строк):
{result_summary}

Объясни результаты понятно и кратко."""

        messages = [
            {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        answer = ollama_service.chat(messages, temperature=0.3)
        return answer


# Singleton
answer_generator = AnswerGenerator()
