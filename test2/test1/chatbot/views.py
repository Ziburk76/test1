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
from chatbot.services.semantic_layer import get_tables_for_question, build_dynamic_schema, get_sample_data

logger = logging.getLogger(__name__)

chat_sessions = {}
text_to_sql = TextToSQL()


def index(request):
    return render(request, 'chat.html')


def tests_page(request):
    return render(request, 'tests.html', {
        'tests_json': json.dumps(TESTS, ensure_ascii=False)
    })


@csrf_exempt
@require_http_methods(["POST"])
def chat(request):
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')

        if not message:
            return JsonResponse({'error': 'Сообщение не может быть пустым'}, status=400)

        if session_id not in chat_sessions:
            chat_sessions[session_id] = {'history': [], 'last_sql': None}
        session = chat_sessions[session_id]

        if not ollama_service.check_connection():
            return JsonResponse({
                'answer': 'Ollama не запущена. Команда: ollama serve',
                'sql': None, 'data': None, 'steps': [],
                'error': 'Ollama connection failed', 'corrections_made': False,
            })

        result = text_to_sql.convert_with_steps(message, db_executor, session.get('history'))
        sql = result['sql']
        db_result = result['data']
        error = result['error']
        steps = result['steps']
        corrections_made = result['corrections_made']

        # Генерируем анализ ответа (LLM объясняет результаты)
        if error:
            answer = f'Ошибка: {error}'
        elif db_result and db_result.get('success'):
            try:
                answer = answer_generator.generate(message, sql, db_result)
            except Exception as e:
                count = db_result.get('count', 0)
                cols = ', '.join(db_result.get('columns', []))
                answer = f'Получено {count} записей. Колонки: {cols}. Результат в таблице ниже.'
        else:
            answer = 'Данных не найдено.'

        session['history'].append({"role": "user", "content": message})
        session['history'].append({"role": "assistant", "content": answer})
        session['last_sql'] = sql

        return JsonResponse({
            'answer': answer,
            'sql': sql,
            'data': {
                'columns': db_result['columns'] if db_result else [],
                'rows': db_result['rows'] if db_result else [],
                'count': db_result['count'] if db_result else 0,
            } if db_result else None,
            'steps': steps,
            'error': error,
            'corrections_made': corrections_made,
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат запроса'}, status=400)
    except Exception as e:
        logger.error(f"Ошибка в chat view: {e}", exc_info=True)
        return JsonResponse({'error': f'Внутренняя ошибка: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def check_connection(request):
    return JsonResponse({
        'ollama_connected': ollama_service.check_connection(),
        'model': settings.OLLAMA_MODEL,
    })


@require_http_methods(["GET"])
def session_info(request):
    session_id = request.GET.get('session_id', 'default')
    if session_id in chat_sessions:
        return JsonResponse({
            'messages_count': len(chat_sessions[session_id]['history']),
            'history': chat_sessions[session_id]['history'],
        })
    return JsonResponse({'messages_count': 0, 'history': []})


@require_http_methods(["GET"])
def debug_schema(request):
    question = request.GET.get('q', '')
    tables, keywords = get_tables_for_question(question)
    schema = build_dynamic_schema(tables) if tables else 'FULL SCHEMA'
    sample_data = get_sample_data(tables, sample_size=2) if tables else ''
    return JsonResponse({
        'question': question,
        'matched_keywords': keywords,
        'tables': sorted(tables) if tables else 'ALL',
        'table_count': len(tables) if tables else 27,
        'schema': schema,
        'sample_data': sample_data,
        'estimated_tokens': round(len((schema + sample_data).split()) * 1.3),
    })


@csrf_exempt
@require_http_methods(["POST"])
def reset_session(request):
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id', 'default')
        if session_id in chat_sessions:
            del chat_sessions[session_id]
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def compare_sql(request):
    try:
        data = json.loads(request.body)
        actual_sql = data.get('actual_sql', '').strip()
        expected_sql = data.get('expected_sql', '').strip()

        if not actual_sql or not expected_sql:
            return JsonResponse({'passed': False, 'reason': 'Нет SQL'})

        actual_result = db_executor.execute(actual_sql)
        expected_result = db_executor.execute(expected_sql)

        if not actual_result['success']:
            return JsonResponse({'passed': False, 'reason': f'Ошибка actual: {actual_result["error"]}',
                                 'actual': {'error': actual_result['error']},
                                 'expected': {'columns': expected_result['columns'], 'count': expected_result['count']}})

        if not expected_result['success']:
            return JsonResponse({'passed': False, 'reason': f'Ошибка expected: {expected_result["error"]}',
                                 'actual': {'columns': actual_result['columns'], 'count': actual_result['count']},
                                 'expected': {'error': expected_result['error']}})

        actual_rows = actual_result.get('rows', [])
        expected_rows = expected_result.get('rows', [])
        actual_count = len(actual_rows)
        expected_count_val = len(expected_rows)

        if actual_count == 0 and expected_count_val == 0:
            return JsonResponse({'passed': True, 'reason': 'Оба пустые',
                                 'actual': {'columns': actual_result['columns'], 'count': 0},
                                 'expected': {'columns': expected_result['columns'], 'count': 0}})

        if actual_count == 0 or expected_count_val == 0:
            return JsonResponse({'passed': False, 'reason': f'actual={actual_count}, expected={expected_count_val}',
                                 'actual': {'columns': actual_result['columns'], 'count': actual_count, 'rows': actual_rows[:5]},
                                 'expected': {'columns': expected_result['columns'], 'count': expected_count_val, 'rows': expected_rows[:5]}})

        def norm(row):
            return tuple(sorted(str(v) for v in row.values()))

        actual_set = set(norm(r) for r in actual_rows)
        expected_set = set(norm(r) for r in expected_rows)
        overlap = len(actual_set & expected_set)
        total = len(actual_set | expected_set)
        similarity = overlap / total if total > 0 else 0

        actual_cols = set(actual_result.get('columns', []))
        expected_cols = set(expected_result.get('columns', []))
        col_sim = len(actual_cols & expected_cols) / len(actual_cols | expected_cols) if (actual_cols | expected_cols) else 0

        if similarity >= 0.8 and col_sim >= 0.3:
            return JsonResponse({'passed': True, 'reason': f'Совпадение {round(similarity*100)}%, колонки {round(col_sim*100)}%',
                                 'actual': {'columns': actual_result['columns'], 'count': actual_count, 'rows': actual_rows[:5]},
                                 'expected': {'columns': expected_result['columns'], 'count': expected_count_val, 'rows': expected_rows[:5]}})
        elif similarity >= 0.5 and col_sim >= 0.3:
            return JsonResponse({'passed': True, 'reason': f'Частичное {round(similarity*100)}%, колонки {round(col_sim*100)}%',
                                 'actual': {'columns': actual_result['columns'], 'count': actual_count, 'rows': actual_rows[:5]},
                                 'expected': {'columns': expected_result['columns'], 'count': expected_count_val, 'rows': expected_rows[:5]}})
        else:
            return JsonResponse({'passed': False, 'reason': f'Не совпадает {round(similarity*100)}%, колонки {round(col_sim*100)}%',
                                 'actual': {'columns': actual_result['columns'], 'count': actual_count, 'rows': actual_rows[:5]},
                                 'expected': {'columns': expected_result['columns'], 'count': expected_count_val, 'rows': expected_rows[:5]}})

    except Exception as e:
        return JsonResponse({'passed': False, 'reason': str(e)})
