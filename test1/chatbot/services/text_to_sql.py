"""
Модуль Text-to-SQL: генерация SQL-запросов из естественного языка.
Использует Dynamic Schema Retrieval — схема подбирается под вопрос.
"""
import re
import logging
from .ollama_service import ollama_service
from .semantic_layer import (
    get_tables_for_question,
    build_dynamic_schema,
    TABLE_SCHEMAS,
    ALL_RELATIONS,
)

logger = logging.getLogger(__name__)

# Полная схема (фоллбэк если ключевые слова не сработали)
FULL_SCHEMA = "\n".join(TABLE_SCHEMAS.values()) + "\n" + ALL_RELATIONS

# Форматирование (одинаковое для любого вопроса)
FORMATTING_RULES = """
ПРАВИЛА ФОРМАТИРОВАНИЯ SQL (СТРОГО СОБЛЮДАЙ):

1. ПСЕВДОНИМЫ ТАБЛИЦ (обязательно):
   - mdc_machine → m
   - mdc_dept → d
   - mdc_machine_param → mp
   - mdc_group_param → gp
   - mdc_machine_param_in_group → mpg
   - mdc_param_in_machine → pm
   - mdc_monitoring_value_129 → mv
   - mdc_operating_program_execution_log → l
   - mdc_operating_program_assembly_unit → opa
   - mdc_shedule_base → sb
   - mdc_shedule_base_item → sbi
   - mdc_shedule_meta → sm
   - mdc_technology_control_setting → tcs
   - mdc_technology_control_log → tcl
   - mdc_technology_control_type → tct
   - hr_worker → w
   - hr_dept → hd
   - rep_monitoring_by_priority → r
   - rep_main_analitic → r
   - tp_assembly_unit → au
   - tp_technology_operation → to

2. ALIAS СТОЛБЦОВ:
   - name станка → m.name AS machine
   - num станка → m.num
   - name цеха → d.name AS dept_name
   - name состояния → mp.name AS state (или mp.name AS param_name)
   - name программы → l.name_up
   - surname → w.surname
   - name сотрудника → w.name
   - time_from/time_to → sbi.time_from, sbi.time_to
   - state_time → r.state_time
   - param_value → tcl.param_value

3. LIMIT: ВСЕГДА добавляй LIMIT 50, если нет GROUP BY.
   Если есть GROUP BY — LIMIT не нужен.

4. НЕ добавляй DISTINCT без явного запроса "уникальные".

5. НЕ добавляй лишних JOIN.

6. ORDER BY: только при "покажи в порядке", "отсортируй", "наибольший"/"меньший".

7. GROUP BY: GROUP BY m.name (не m.id).

8. Формат: одна строка, без переносов.

9. Возвращай ТОЛЬКО SQL, без markdown, без пояснений.
"""

# Few-shot примеры
FEW_SHOT_EXAMPLES = """
ПРИМЕРЫ ЗАПРОСОВ:

Вопрос: "Какие станки есть на заводе?"
SQL: SELECT name, num, oeeplan FROM mdc_machine LIMIT 50

Вопрос: "Покажи станки с указанием их цеха"
SQL: SELECT m.name, m.num, d.name AS dept_name FROM mdc_machine m JOIN mdc_dept d ON m.dept_id = d.id LIMIT 50

Вопрос: "Какие программы выполнялись на станках?"
SQL: SELECT m.name AS machine, l.name_up, l.dt_start, l.dt_end, l.processing_time FROM mdc_operating_program_execution_log l JOIN mdc_machine m ON l.machine_id = m.id LIMIT 50

Вопрос: "Кто и какие программы выполнял на станках?"
SQL: SELECT m.name AS machine, w.surname, w.name, l.name_up, l.dt_start, l.processing_time FROM mdc_operating_program_execution_log l JOIN mdc_machine m ON l.machine_id = m.id JOIN hr_worker w ON l.worker_id = w.id LIMIT 50

Вопрос: "Какое общее время простоев у каждого станка?"
SQL: SELECT m.name AS machine, SUM(r.state_time) AS total_downtime_seconds FROM rep_monitoring_by_priority r JOIN mdc_machine m ON r.mdc_machineid = m.id JOIN mdc_machine_param mp ON r.mdc_machine_param_id = mp.id WHERE mp.id IN (SELECT mdc_machine_param_id FROM mdc_machine_param_in_group WHERE mdc_group_param_id IN (SELECT id FROM mdc_group_param WHERE name LIKE '%Простой%')) GROUP BY m.name

Вопрос: "Сколько программ выполнено на каждом станке?"
SQL: SELECT m.name AS machine, COUNT(l.id) AS program_count, SUM(l.processing_time) AS total_time FROM mdc_operating_program_execution_log l JOIN mdc_machine m ON l.machine_id = m.id GROUP BY m.name

Вопрос: "Покажи расписание работы станков"
SQL: SELECT m.name AS machine, sb.name, sb.week_day_num, sb.smena_num, sbi.time_from, sbi.time_to FROM mdc_shedule_base sb JOIN mdc_machine m ON sb.machine_id = m.id JOIN mdc_shedule_base_item sbi ON sb.id = sbi.shedule_base_id LIMIT 50

Вопрос: "Покажи историю состояний станков"
SQL: SELECT m.name AS machine, mp.name AS state, mv.start_time, mv.end_time FROM mdc_monitoring_value_129 mv JOIN mdc_machine m ON mv.machine_id = m.id JOIN mdc_machine_param mp ON mv.machine_param_id = mp.id LIMIT 50
"""


def build_system_prompt(question: str) -> str:
    """
    Построить системный промпт с динамической схемой под вопрос.
    """
    # Определяем нужные таблицы
    tables, keywords = get_tables_for_question(question)

    if tables:
        # Dynamic schema
        schema = build_dynamic_schema(tables)
        schema_note = f"\n\nРЕЛЕВАНТНЫЕ ТАБЛИЦЫ (найдены по ключевым словам: {', '.join(keywords)}):\n"
    else:
        # Full schema fallback
        schema = FULL_SCHEMA
        schema_note = "\n\nПОЛНАЯ СХЕМА БАЗЫ ДАННЫХ:\n"

    return f"""Ты — генератор SQL-запросов к базе данных производственного предприятия.
Принимаешь вопрос на русском языке → возвращаешь SQL SELECT.{schema_note}
{schema}

{FORMATTING_RULES}

{FEW_SHOT_EXAMPLES}

ИТОГОВОЕ ПРАВИЛО: возвращай СТРОГО ОДНУ СТРОКУ — SQL-запрос. Никаких markdown, никаких пояснений.
Если вопрос невозможно перевести в SQL → ответь: "НЕВОЗМОЖНО: причина"
"""


class TextToSQL:
    """Конвертирует естественный язык в SQL-запросы."""

    MAX_RETRIES = 1

    def convert(self, question: str, conversation_history: list = None) -> str:
        # Строим промпт с динамической схемой
        system_prompt = build_system_prompt(question)

        messages = [{"role": "system", "content": system_prompt}]

        if conversation_history:
            for msg in conversation_history[-5:]:
                messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": question})

        sql = ollama_service.chat(messages, temperature=0.1)
        sql = self._clean_sql(sql)

        is_valid, error = self._validate_sql(sql)
        if not is_valid:
            logger.warning(f"Невалидный SQL: {error}. Запрос: {sql}")
            if self.MAX_RETRIES > 0:
                messages.append({"role": "assistant", "content": sql})
                messages.append({"role": "user", "content": f"Ошибка: {error}. Исправь и верни ТОЛЬКО SQL одной строкой."})
                sql = ollama_service.chat(messages, temperature=0.05)
                sql = self._clean_sql(sql)

        return sql

    def _clean_sql(self, raw_sql: str) -> str:
        sql = raw_sql.strip()
        sql = re.sub(r'^```sql\s*', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'^```\s*', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'\s*```$', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'\s*\n\s*', ' ', sql)
        sql = re.sub(r' {2,}', ' ', sql)
        sql = sql.strip()
        if sql.endswith(';'):
            sql = sql[:-1].strip()
        sql = re.sub(r'\s+LIMIT\s*$', '', sql, flags=re.IGNORECASE)
        sql = re.sub(r'\s+LIMIT\s+0\s*$', '', sql, flags=re.IGNORECASE)
        return sql

    def _validate_sql(self, sql: str) -> tuple:
        sql_upper = sql.upper().strip()
        dangerous = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE']
        for kw in dangerous:
            if kw in sql_upper:
                return False, f"Опасная команда: {kw}"
        if not sql_upper.startswith('SELECT'):
            return False, "Должен начинаться с SELECT"
        if len(sql) < 10:
            return False, "Слишком короткий"
        if sql_upper.startswith('НЕВОЗМОЖНО') or sql_upper.startswith('НЕВОЗМОЖНО:'):
            return False, sql
        return True, ""
