"""
Views для чат-бота ИИ-ассистента.
"""
import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings

from chatbot.services.ollama_service import ollama_service
from chatbot.services.text_to_sql import TextToSQL
from chatbot.services.db_executor import db_executor
from chatbot.services.answer_generator import answer_generator
from chatbot.test_data import TESTS
from chatbot.services.semantic_layer import get_tables_for_question, build_dynamic_schema

logger = logging.getLogger(__name__)

# Хранилище сессий в памяти (в production заменить на БД/Redis)
chat_sessions = {}

text_to_sql = TextToSQL()


def index(request):
    """Главная страница чат-бота."""
    return render(request, 'chat.html')


def tests_page(request):
    """Страница автоматических тестов."""
    return render(request, 'tests.html', {
        'tests_json': json.dumps(TESTS, ensure_ascii=False)
    })


@csrf_exempt
@require_http_methods(["POST"])
def chat(request):
    """
    Обработка сообщения чата.
    
    Request JSON:
        {
            "message": "текст вопроса",
            "session_id": "идентификатор сессии"
        }
    
    Response JSON:
        {
            "answer": "текст ответа",
            "sql": "сгенерированный SQL",
            "data": {...результаты SQL...},
            "error": null или текст ошибки
        }
    """
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')

        if not message:
            return JsonResponse({'error': 'Сообщение не может быть пустым'}, status=400)

        # Получаем или создаём сессию
        if session_id not in chat_sessions:
            chat_sessions[session_id] = {
                'history': [],
                'last_sql': None,
            }
        session = chat_sessions[session_id]

        # Проверяем подключение к Ollama
        if not ollama_service.check_connection():
            return JsonResponse({
                'answer': '❌ Не удалось подключиться к Ollama. Убедитесь, что Ollama запущен командой:\n\n```\nollama serve\n```',
                'sql': None,
                'data': None,
                'error': 'Ollama connection failed',
            })

        # Генерируем SQL
        sql = text_to_sql.convert(message, session.get('history'))

        if sql.upper().startswith('НЕВОЗМОЖНО'):
            # LLM не смогла составить запрос
            answer = sql.replace('НЕВОЗМОЖНО:', '').replace('НЕВОЗМОЖНО', '').strip()
            session['history'].append({"role": "user", "content": message})
            session['history'].append({"role": "assistant", "content": answer})
            return JsonResponse({
                'answer': f"🤔 {answer}",
                'sql': None,
                'data': None,
                'error': None,
            })

        # Выполняем SQL
        db_result = db_executor.execute(sql)

        if not db_result['success']:
            error_msg = db_result.get('error', 'Неизвестная ошибка БД')
            session['history'].append({"role": "user", "content": message})
            session['history'].append({"role": "assistant", "content": f"Ошибка: {error_msg}"})
            return JsonResponse({
                'answer': f"❌ {error_msg}",
                'sql': sql,
                'data': None,
                'error': error_msg,
            })

        # Генерируем понятный ответ
        answer = answer_generator.generate(message, sql, db_result)

        # Сохраняем в историю
        session['history'].append({"role": "user", "content": message})
        session['history'].append({"role": "assistant", "content": answer})
        session['last_sql'] = sql

        return JsonResponse({
            'answer': answer,
            'sql': sql,
            'data': {
                'columns': db_result['columns'],
                'rows': db_result['rows'],
                'count': db_result['count'],
            },
            'error': None,
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат запроса'}, status=400)
    except Exception as e:
        logger.error(f"Ошибка в chat view: {e}", exc_info=True)
        return JsonResponse({'error': f'Внутренняя ошибка сервера: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def check_connection(request):
    """Проверка подключения к Ollama."""
    is_connected = ollama_service.check_connection()
    return JsonResponse({
        'ollama_connected': is_connected,
        'model': settings.OLLAMA_MODEL,
    })


@require_http_methods(["GET"])
def session_info(request):
    """Информация о текущей сессии."""
    session_id = request.GET.get('session_id', 'default')
    if session_id in chat_sessions:
        session = chat_sessions[session_id]
        return JsonResponse({
            'messages_count': len(session['history']),
            'history': session['history'],
        })
    return JsonResponse({'messages_count': 0, 'history': []})


@require_http_methods(["GET"])
def debug_schema(request):
    """Показать какие таблицы выбраны для вопроса (отладка dynamic schema)."""
    question = request.GET.get('q', '')
    tables, keywords = get_tables_for_question(question)
    schema = build_dynamic_schema(tables) if tables else 'FULL SCHEMA (fallback)'
    token_estimate = len(schema.split()) * 1.3
    return JsonResponse({
        'question': question,
        'matched_keywords': keywords,
        'tables': sorted(tables) if tables else 'ALL TABLES',
        'table_count': len(tables) if tables else 27,
        'schema': schema,
        'estimated_tokens': round(token_estimate),
    })


@csrf_exempt
@require_http_methods(["POST"])
def reset_session(request):
    """Сбросить сессию (очистить историю)."""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id', 'default')
        if session_id in chat_sessions:
            del chat_sessions[session_id]
        return JsonResponse({'status': 'ok', 'message': 'Сессия сброшена'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def compare_sql(request):
    """
    Семантическая валидация SQL: выполнить оба запроса и сравнить результаты.
    
    Request JSON:
        {
            "actual_sql": "SELECT ...",
            "expected_sql": "SELECT ...",
            "expected_count": 3  // опционально
        }
    
    Response JSON:
        {
            "passed": true/false,
            "reason": "...",
            "actual": {"columns": [...], "rows": [...], "count": N},
            "expected": {"columns": [...], "rows": [...], "count": N}
        }
    """
    try:
        data = json.loads(request.body)
        actual_sql = data.get('actual_sql', '').strip()
        expected_sql = data.get('expected_sql', '').strip()
        expected_count = data.get('expected_count')

        if not actual_sql or not expected_sql:
            return JsonResponse({'passed': False, 'reason': 'Нет SQL для сравнения'})

        # Выполняем оба запроса
        actual_result = db_executor.execute(actual_sql)
        expected_result = db_executor.execute(expected_sql)

        if not actual_result['success']:
            return JsonResponse({
                'passed': False,
                'reason': f'Ошибка actual SQL: {actual_result["error"]}',
                'actual': {'error': actual_result['error']},
                'expected': {'columns': expected_result['columns'], 'count': expected_result['count']}
            })

        if not expected_result['success']:
            return JsonResponse({
                'passed': False,
                'reason': f'Ошибка expected SQL: {expected_result["error"]}',
                'actual': {'columns': actual_result['columns'], 'count': actual_result['count']},
                'expected': {'error': expected_result['error']}
            })

        actual_rows = actual_result.get('rows', [])
        expected_rows = expected_result.get('rows', [])
        actual_count = len(actual_rows)
        expected_count_val = len(expected_rows)

        # Если оба пустые — это совпадение
        if actual_count == 0 and expected_count_val == 0:
            return JsonResponse({
                'passed': True,
                'reason': 'Оба запроса вернули пустой результат',
                'actual': {'columns': actual_result['columns'], 'count': 0},
                'expected': {'columns': expected_result['columns'], 'count': 0}
            })

        # Если один пустой, а другой нет
        if actual_count == 0 or expected_count_val == 0:
            return JsonResponse({
                'passed': False,
                'reason': f'Несовпадение: actual={actual_count} строк, expected={expected_count_val} строк',
                'actual': {'columns': actual_result['columns'], 'count': actual_count, 'rows': actual_rows[:5]},
                'expected': {'columns': expected_result['columns'], 'count': expected_count_val, 'rows': expected_rows[:5]}
            })

        # Сравнение по количеству строк (с допуском)
        count_match = actual_count == expected_count_val

        # Сравнение по содержимому — извлекаем только значения (без ключей), сортируем
        def normalize_row(row):
            return tuple(sorted(str(v) for v in row.values()))

        actual_set = set(normalize_row(r) for r in actual_rows)
        expected_set = set(normalize_row(r) for r in expected_rows)

        # Проверяем пересечение
        overlap = len(actual_set & expected_set)
        total = len(actual_set | expected_set)
        similarity = overlap / total if total > 0 else 0

        # Проверяем, что все ожидаемые строки есть в actual
        all_expected_present = expected_set.issubset(actual_set)
        # Или наоборот
        all_actual_in_expected = actual_set.issubset(expected_set)

        # Проверяем совпадение колонок (хотя бы частичное)
        actual_cols = set(actual_result.get('columns', []))
        expected_cols = set(expected_result.get('columns', []))
        col_overlap = len(actual_cols & expected_cols)
        col_total = len(actual_cols | expected_cols)
        col_similarity = col_overlap / col_total if col_total > 0 else 0

        # Итоговая оценка
        if similarity >= 0.8 and col_similarity >= 0.3:
            return JsonResponse({
                'passed': True,
                'reason': f'Результаты совпадают (сходство {round(similarity * 100)}%, колонки {round(col_similarity * 100)}%)',
                'actual': {'columns': actual_result['columns'], 'count': actual_count, 'rows': actual_rows[:5]},
                'expected': {'columns': expected_result['columns'], 'count': expected_count_val, 'rows': expected_rows[:5]}
            })
        elif similarity >= 0.5 and col_similarity >= 0.3:
            return JsonResponse({
                'passed': True,
                'reason': f'Частичное совпадение (сходство {round(similarity * 100)}%, колонки {round(col_similarity * 100)}%)',
                'actual': {'columns': actual_result['columns'], 'count': actual_count, 'rows': actual_rows[:5]},
                'expected': {'columns': expected_result['columns'], 'count': expected_count_val, 'rows': expected_rows[:5]}
            })
        else:
            return JsonResponse({
                'passed': False,
                'reason': f'Результаты не совпадают (сходство {round(similarity * 100)}%, колонки {round(col_similarity * 100)}%)',
                'actual': {'columns': actual_result['columns'], 'count': actual_count, 'rows': actual_rows[:5]},
                'expected': {'columns': expected_result['columns'], 'count': expected_count_val, 'rows': expected_rows[:5]}
            })

    except json.JSONDecodeError:
        return JsonResponse({'passed': False, 'reason': 'Неверный формат запроса'})
    except Exception as e:
        return JsonResponse({'passed': False, 'reason': f'Ошибка: {str(e)}'})
