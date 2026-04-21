import json
import logging
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q

from chatbot.services.ollama_service import ollama_service
from chatbot.services.text_to_sql import TextToSQL
from chatbot.services.db_executor import db_executor
from chatbot.services.answer_generator import answer_generator
from chatbot.test_data import TESTS
from chatbot.services.semantic_layer import get_tables_for_question, build_dynamic_schema
from chatbot.models import ChatSession, ChatMessage

logger = logging.getLogger(__name__)

# Хранилище сессий в памяти (в production заменить на БД/Redis)
chat_sessions = {}

text_to_sql = TextToSQL()


def index(request):
    """Главная страница чат-бота."""
    if request.user.is_authenticated:
        return redirect('chat')
    return redirect('login')


def login_view(request):
    """Страница входа."""
    if request.user.is_authenticated:
        return redirect('chat')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'chat')
            return redirect(next_url)
        else:
            messages_error = "Неверный логин или пароль"
            return render(request, 'login.html', {'error': messages_error})
    
    return render(request, 'login.html')


def register_view(request):
    """Страница регистрации."""
    if request.user.is_authenticated:
        return redirect('chat')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        
        if not username or not password:
            return render(request, 'register.html', {'error': 'Заполните все поля'})
        
        if password != password_confirm:
            return render(request, 'register.html', {'error': 'Пароли не совпадают'})
        
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Пользователь уже существует'})
        
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('chat')
    
    return render(request, 'register.html')


@login_required
def logout_view(request):
    """Выход из системы."""
    logout(request)
    return redirect('login')


@login_required
def chat(request):
    """Страница чата."""
    # Получаем все сессии пользователя
    sessions = ChatSession.objects.filter(user=request.user)
    current_session_id = request.GET.get('session_id')
    
    context = {
        'sessions': sessions,
        'current_session_id': current_session_id,
        'user': request.user,
    }
    return render(request, 'chat.html', context)


@login_required
@require_http_methods(["POST"])
def create_session(request):
    """Создать новую сессию чата."""
    session_name = request.POST.get('session_name', 'Новый чат')
    session = ChatSession.objects.create(user=request.user, session_name=session_name)
    return redirect('chat')


@login_required
@require_http_methods(["DELETE"])
def delete_session(request, session_id):
    """Удалить сессию."""
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    session.delete()
    return JsonResponse({'status': 'ok'})


@login_required
@require_http_methods(["GET"])
def load_session_history(request, session_id):
    """Загрузить историю сообщений сессии."""
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    messages = ChatMessage.objects.filter(session=session).order_by('created_at')
    
    history = []
    for msg in messages:
        history.append({
            'role': msg.role,
            'content': msg.content,
            'created_at': msg.created_at.isoformat(),
        })
    
    return JsonResponse({
        'session_id': str(session.id),
        'session_name': session.session_name,
        'history': history,
    })


def tests_page(request):
    """Страница автоматических тестов."""
    return render(request, 'tests.html', {
        'tests_json': json.dumps(TESTS, ensure_ascii=False)
    })


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """
    Обработка сообщения чата (API).
    
    Request JSON:
        {
            "message": "текст вопроса",
            "session_id": "идентификатор сессии" (UUID, опционально)
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
        session_id = data.get('session_id')

        if not message:
            return JsonResponse({'error': 'Сообщение не может быть пустым'}, status=400)

        # Получаем или создаём сессию в БД
        if session_id:
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        else:
            # Создаём новую сессию
            session = ChatSession.objects.create(user=request.user, session_name=message[:50])
            session_id = str(session.id)

        # Получаем историю из БД
        db_messages = ChatMessage.objects.filter(session=session).order_by('created_at')
        history = [{'role': msg.role, 'content': msg.content} for msg in db_messages]

        # Проверяем подключение к Ollama
        if not ollama_service.check_connection():
            return JsonResponse({
                'answer': '❌ Не удалось подключиться к Ollama. Убедитесь, что Ollama запущен командой:\n\n```\nollama serve\n```',
                'sql': None,
                'data': None,
                'error': 'Ollama connection failed',
            })

        # Генерируем SQL
        raw_sql = text_to_sql.convert(message, history)

        # --- ПУНКТ 2: Умный парсинг ответа LLM ---
        # Извлекаем чистый SQL из ответа модели (даже если он в тексте или markdown)
        sql = extract_sql_from_response(raw_sql)
        
        if not sql:
            answer = "Не удалось распознать SQL-запрос в ответе модели."
            ChatMessage.objects.create(session=session, role='user', content=message)
            ChatMessage.objects.create(session=session, role='assistant', content=answer)
            return JsonResponse({
                'answer': f"🤔 {answer}",
                'sql': raw_sql,
                'data': None,
                'error': 'SQL parsing failed',
                'session_id': session_id,
            })

        # --- ПУНКТ 1: Жесткая фильтрация SQL ---
        # Проверка безопасности: разрешаем только SELECT
        sql_upper = sql.upper().strip()
        forbidden_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        for keyword in forbidden_keywords:
            if keyword in sql_upper:
                answer = f"⛔ Запрос содержит запрещённую операцию ({keyword}). Разрешены только SELECT-запросы."
                ChatMessage.objects.create(session=session, role='user', content=message)
                ChatMessage.objects.create(session=session, role='assistant', content=answer)
                return JsonResponse({
                    'answer': answer,
                    'sql': sql,
                    'data': None,
                    'error': 'Forbidden SQL operation',
                    'session_id': session_id,
                })
        
        if not sql_upper.startswith('SELECT'):
            answer = "⛔ Запрос должен начинаться с SELECT."
            ChatMessage.objects.create(session=session, role='user', content=message)
            ChatMessage.objects.create(session=session, role='assistant', content=answer)
            return JsonResponse({
                'answer': answer,
                'sql': sql,
                'data': None,
                'error': 'Only SELECT allowed',
                'session_id': session_id,
            })

        # Автоматически добавляем LIMIT 50, если его нет
        if 'LIMIT' not in sql_upper:
            sql = sql.rstrip(';') + ' LIMIT 50'

        if sql.upper().startswith('НЕВОЗМОЖНО'):
            # LLM не смогла составить запрос
            answer = sql.replace('НЕВОЗМОЖНО:', '').replace('НЕВОЗМОЖНО', '').strip()
            # Сохраняем в БД
            ChatMessage.objects.create(session=session, role='user', content=message)
            ChatMessage.objects.create(session=session, role='assistant', content=answer)
            return JsonResponse({
                'answer': f"🤔 {answer}",
                'sql': None,
                'data': None,
                'error': None,
                'session_id': session_id,
            })

        # Выполняем SQL
        db_result = db_executor.execute(sql)

        # --- ПУНКТ 3: Авто-исправление ошибок ---
        if not db_result['success']:
            error_msg = db_result.get('error', 'Неизвестная ошибка БД')
            
            # Попытка авто-исправления (один раз)
            correction_prompt = (
                f"Запрос не выполнился. Ошибка базы данных: {error_msg}. "
                f"Исходный запрос: {sql}. "
                f"Исправь SQL-запрос и верни ТОЛЬКО код SQL без объяснений."
            )
            corrected_sql = ollama_service.generate_sql(correction_prompt, history)
            
            # Парсим и проверяем исправленный запрос
            corrected_sql = extract_sql_from_response(corrected_sql)
            
            if corrected_sql and 'LIMIT' not in corrected_sql.upper():
                corrected_sql = corrected_sql.rstrip(';') + ' LIMIT 50'
            
            retry_result = None
            if corrected_sql and corrected_sql != sql:
                # Проверяем безопасность исправленного запроса
                corrected_upper = corrected_sql.upper().strip()
                is_safe = not any(k in corrected_upper for k in forbidden_keywords) and corrected_upper.startswith('SELECT')
                if is_safe:
                    retry_result = db_executor.execute(corrected_sql)
            
            if retry_result and retry_result['success']:
                # Исправление успешно!
                sql = corrected_sql
                db_result = retry_result
                answer = answer_generator.generate(message, sql, db_result)
                ChatMessage.objects.create(session=session, role='user', content=message)
                ChatMessage.objects.create(session=session, role='assistant', content=f"{answer}\n\n*(Запрос был автоматически исправлен)*")
                return JsonResponse({
                    'answer': answer,
                    'sql': sql,
                    'data': {
                        'columns': db_result['columns'],
                        'rows': db_result['rows'],
                        'count': db_result['count'],
                    },
                    'error': None,
                    'session_id': session_id,
                })
            else:
                # Исправление не помогло или невозможно
                answer = f"❌ Ошибка выполнения запроса: {error_msg}"
                ChatMessage.objects.create(session=session, role='user', content=message)
                ChatMessage.objects.create(session=session, role='assistant', content=answer)
                return JsonResponse({
                    'answer': answer,
                    'sql': sql,
                    'data': None,
                    'error': error_msg,
                    'session_id': session_id,
                })

        # Генерируем понятный ответ
        answer = answer_generator.generate(message, sql, db_result)

        # Сохраняем в БД
        ChatMessage.objects.create(session=session, role='user', content=message)
        ChatMessage.objects.create(session=session, role='assistant', content=answer)

        return JsonResponse({
            'answer': answer,
            'sql': sql,
            'data': {
                'columns': db_result['columns'],
                'rows': db_result['rows'],
                'count': db_result['count'],
            },
            'error': None,
            'session_id': session_id,
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат запроса'}, status=400)
    except Exception as e:
        logger.error(f"Ошибка в chat_api view: {e}", exc_info=True)
        return JsonResponse({'error': f'Внутренняя ошибка сервера: {str(e)}'}, status=500)


def extract_sql_from_response(response_text):
    """
    Извлекает чистый SQL-запрос из текста ответа LLM.
    Ищет запрос внутри ```sql ... ``` или просто первый валидный SELECT.
    """
    if not response_text:
        return None
    
    response_text = response_text.strip()
    
    # Если ответ начинается с явного маркера невозможности
    if response_text.upper().startswith('НЕВОЗМОЖНО'):
        return response_text
    
    # Паттерн 1: Поиск внутри ```sql ... ``` или ``` ... ```
    code_block_pattern = r'```(?:sql)?\s*(.*?)\s*```'
    matches = re.findall(code_block_pattern, response_text, re.IGNORECASE | re.DOTALL)
    if matches:
        sql = matches[0].strip()
        # Убираем возможные лишние точки с запятой в конце
        return sql.rstrip(';')
    
    # Паттерн 2: Поиск первого SELECT ... до точки с запятой или конца строки
    select_pattern = r'(SELECT\s+.*?)(?:;|$)'
    match = re.search(select_pattern, response_text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip().rstrip(';')
    
    # Паттерн 3: Если текст просто похож на SQL (начинается с SELECT)
    if response_text.upper().strip().startswith('SELECT'):
        return response_text.strip().rstrip(';')
    
    # Ничего не найдено
    return None


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
