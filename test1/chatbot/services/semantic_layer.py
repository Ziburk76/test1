"""
Семантический слой — словарь бизнес-терминов для маппинга
пользовательских понятий на таблицы и столбцы БД.
"""

# === KEYWORD → TABLES маппинг для Dynamic Schema Retrieval ===
# Каждый пользовательский термин маппится на набор таблиц, которые нужны для ответа.
# При совпадении нескольких ключей — таблицы объединяются (set union).
KEYWORD_TABLE_MAP = {
    # --- Станки и оборудование ---
    "станк": ["mdc_machine", "mdc_dept"],
    "оборуд": ["mdc_machine", "mdc_dept"],
    "машин": ["mdc_machine"],
    "цех": ["mdc_machine", "mdc_dept", "hr_dept"],
    "подразделен": ["mdc_dept", "hr_dept"],
    "участок": ["mdc_dept"],
    "оее": ["mdc_machine"],
    "oee": ["mdc_machine"],
    "ввод в эксплуат": ["mdc_machine"],

    # --- Состояния и простои ---
    "простой": ["rep_monitoring_by_priority", "mdc_machine", "mdc_machine_param", "mdc_group_param"],
    "простои": ["rep_monitoring_by_priority", "mdc_machine", "mdc_machine_param", "mdc_group_param"],
    "состоян": ["mdc_machine_param", "mdc_group_param", "mdc_machine_param_in_group"],
    "групп": ["mdc_group_param", "mdc_machine_param_in_group"],
    "приоритет": ["mdc_machine_param", "rep_monitoring_by_priority"],
    "код состоян": ["mdc_machine_param"],

    # --- Программы и выполнение ---
    "программ": ["mdc_operating_program_execution_log", "mdc_machine"],
    "выполнен": ["mdc_operating_program_execution_log", "mdc_machine"],
    "управляющ": ["mdc_operating_program_execution_log"],
    "name_up": ["mdc_operating_program_execution_log", "mdc_operating_program_assembly_unit"],

    # --- Расписание ---
    "расписан": ["mdc_shedule_base", "mdc_shedule_base_item", "mdc_shedule_meta", "mdc_machine"],
    "смен": ["mdc_shedule_base"],
    "праздник": ["mdc_shedule_meta"],
    "врем": ["mdc_shedule_base_item"],
    "график": ["mdc_shedule_base", "mdc_shedule_base_item"],

    # --- Детали и техпроцессы ---
    "детал": ["tp_assembly_unit", "mdc_operating_program_assembly_unit"],
    "сборочн": ["tp_assembly_unit", "mdc_operating_program_assembly_unit"],
    "операци": ["tp_technology_operation"],
    "технологи": ["tp_technology_operation"],
    "штучн": ["tp_technology_operation"],
    "машинн": ["tp_technology_operation"],

    # --- Контроль параметров ---
    "контрол": ["mdc_technology_control_setting", "mdc_technology_control_log"],
    "нарушен": ["mdc_technology_control_log", "mdc_param_in_machine", "mdc_machine"],
    "настройк": ["mdc_technology_control_setting", "mdc_group_param"],
    "допуск": ["mdc_technology_control_type"],
    "параметр": ["mdc_machine_param", "mdc_param_in_machine"],
    "отслеж": ["mdc_param_in_machine", "mdc_machine"],

    # --- История состояний ---
    "истори": ["mdc_monitoring_value_129", "mdc_machine", "mdc_machine_param"],
    "начал": ["mdc_monitoring_value_129"],
    "конец": ["mdc_monitoring_value_129"],
    "интервал": ["mdc_monitoring_value_129"],

    # --- Аналитика ---
    "аналитик": ["rep_main_analitic", "hr_dept"],
    "сводн": ["rep_main_analitic"],
    "мониторинг": ["rep_monitoring_by_priority", "mdc_machine"],
    "дневн": ["rep_daily_worker_analytic"],
    "загруз": ["rep_main_analitic"],
    "фонд": ["rep_main_analitic"],
    "производит": ["rep_daily_worker_analytic"],

    # --- Персонал (для JOIN к оборудованию) ---
    "сотрудник": ["hr_worker"],
    "работник": ["hr_worker"],
    "фамил": ["hr_worker"],
    "оператор": ["hr_worker", "mdc_operating_program_execution_log"],
    "наладчик": ["hr_worker"],
    "кто.*работ": ["hr_worker", "mdc_operating_program_execution_log", "mdc_machine"],
    "должност": ["hr_work_position"],
    "професс": ["hr_worker"],
    "табель": ["hr_worker", "hr_time_sheet"],
    "трудозатрат": ["hr_time_sheet", "hr_worker"],
    "увольнен": ["hr_worker", "hr_worker_fired_dept", "hr_transfers_personnel"],
    "принят": ["hr_worker", "hr_transfers_personnel"],
    "текучесть": ["hr_worker_fired_dept"],
    "кадр": ["hr_transfers_personnel"],

    # --- Общие запросы ---
    "какие.*есть": None,  # фоллбэк — полная схема
    "покажи": None,
    "сколько": None,
    "какой": None,
}

# --- Полные схемы для каждого блока таблиц ---
TABLE_SCHEMAS = {
    "mdc_machine": "mdc_machine: id, name, num, short_name, dept_id, _root_num_x, dt_commissioning, oeeplan",
    "mdc_dept": "mdc_dept: id, name, parent_id",
    "mdc_machine_param": "mdc_machine_param: id, name, short_name, parent_id, priority, code, is_service_state",
    "mdc_group_param": "mdc_group_param: id, name, parent_id, short_name, color, plan_value",
    "mdc_machine_param_in_group": "mdc_machine_param_in_group: id, mdc_machine_param_id, mdc_group_param_id",
    "mdc_param_in_machine": "mdc_param_in_machine: id, machine_id, machine_param_id",
    "mdc_monitoring_value_129": "mdc_monitoring_value_129: id, machine_id, start_time, end_time, param_in_machine_id, machine_param_id",
    "mdc_operating_program_execution_log": "mdc_operating_program_execution_log: id, machine_id, worker_id, name_up, dt_start, dt_end, processing_time",
    "mdc_operating_program_assembly_unit": "mdc_operating_program_assembly_unit: id, machine_id, name_up, id_assembly_unit",
    "mdc_shedule_base": "mdc_shedule_base: id, name, week_day_num, smena_num, dept_id, machine_id, shedule_meta_id",
    "mdc_shedule_base_item": "mdc_shedule_base_item: id, shedule_base_id, time_from, time_to",
    "mdc_shedule_meta": "mdc_shedule_meta: id, is_holiday, shedule_date, dept_id, machine_id",
    "mdc_technology_control_setting": "mdc_technology_control_setting: id, name, group_param_id, machine_param_id",
    "mdc_technology_control_log": "mdc_technology_control_log: id, technology_control_setting_id, param_in_machine_id, param_value, dt_start, dt_end, technology_operation_id",
    "mdc_technology_control_type": "mdc_technology_control_type: id, technology_control_setting_id, type_id, is_tolerance, is_emergency",
    "hr_worker": "hr_worker: id, surname, name, patronymic, personal_num, hr_dept_id, dept_num, prof_name, dt_accept, dt_fired, is_deleted",
    "hr_dept": "hr_dept: id, name, parent_id, root_num",
    "hr_work_position": "hr_work_position: id, name",
    "hr_time_sheet": "hr_time_sheet: id, dt_day, hr_worker_id, hr_time_sheet_type_id, time",
    "hr_transfers_personnel": "hr_transfers_personnel: id, unique_code, hr_dept_id, dept_num, tab_num, dt_accept, dt_fired, is_type",
    "hr_worker_fired_dept": "hr_worker_fired_dept: id, dt_day, dept_num, begin_month_num, worker_fired_num, average_headcount_perscent",
    "rep_monitoring_by_priority": "rep_monitoring_by_priority: id, mdc_machineid, mdc_machine_param_id, from_date, to_date, state_time, shift_num, dt_calc",
    "rep_main_analitic": "rep_main_analitic: id, dept_num, dt_of_month, hr_fund_time, hr_lose_time, hr_people_count, mdc_machine_load_time, mdc_machine_break_time, mdc_machine_fund",
    "rep_daily_worker_analytic": "rep_daily_worker_analytic: id, dt_day, hr_worker_id, hr_work_position_id, dept_num, work_time, manufactured_parts_log_count, downtime, fond",
    "tp_assembly_unit": "tp_assembly_unit: id, name",
    "tp_technology_operation": "tp_technology_operation: id, code, description, machine_time, piece_time",
}

# Связи между таблицами (для автодобавления JOIN-таблиц)
TABLE_DEPENDENCIES = {
    "mdc_machine": ["mdc_dept"],
    "mdc_operating_program_execution_log": ["mdc_machine", "hr_worker"],
    "mdc_operating_program_assembly_unit": ["mdc_machine", "tp_assembly_unit"],
    "mdc_monitoring_value_129": ["mdc_machine", "mdc_machine_param"],
    "mdc_param_in_machine": ["mdc_machine", "mdc_machine_param"],
    "mdc_machine_param_in_group": ["mdc_machine_param", "mdc_group_param"],
    "mdc_shedule_base": ["mdc_machine", "mdc_dept"],
    "mdc_shedule_base_item": ["mdc_shedule_base"],
    "mdc_shedule_meta": ["mdc_machine", "mdc_dept"],
    "mdc_technology_control_log": ["mdc_param_in_machine", "mdc_machine"],
    "mdc_technology_control_setting": ["mdc_group_param", "mdc_machine_param"],
    "rep_monitoring_by_priority": ["mdc_machine", "mdc_machine_param"],
    "rep_main_analitic": ["hr_dept"],
    "rep_daily_worker_analytic": ["hr_worker"],
    "hr_worker": ["hr_dept"],
    "hr_time_sheet": ["hr_worker"],
    "hr_transfers_personnel": ["hr_dept"],
    "hr_worker_fired_dept": [],
}

# Полные связи для финального промпта
ALL_RELATIONS = """
Связи:
- mdc_machine.dept_id = mdc_dept.id
- mdc_operating_program_execution_log.machine_id = mdc_machine.id
- mdc_operating_program_execution_log.worker_id = hr_worker.id
- mdc_monitoring_value_129.machine_id = mdc_machine.id
- mdc_monitoring_value_129.machine_param_id = mdc_machine_param.id
- rep_monitoring_by_priority.mdc_machineid = mdc_machine.id
- rep_monitoring_by_priority.mdc_machine_param_id = mdc_machine_param.id
- rep_main_analitic.dept_num = hr_dept.root_num
- rep_daily_worker_analytic.hr_worker_id = hr_worker.id
- mdc_param_in_machine.machine_id = mdc_machine.id
- mdc_param_in_machine.machine_param_id = mdc_machine_param.id
- mdc_machine_param_in_group.mdc_machine_param_id = mdc_machine_param.id
- mdc_machine_param_in_group.mdc_group_param_id = mdc_group_param.id
- mdc_operating_program_assembly_unit.machine_id = mdc_machine.id
- mdc_operating_program_assembly_unit.id_assembly_unit = tp_assembly_unit.id
- mdc_shedule_base.machine_id = mdc_machine.id
- mdc_shedule_base.dept_id = mdc_dept.id
- mdc_shedule_base_item.shedule_base_id = mdc_shedule_base.id
- mdc_technology_control_log.param_in_machine_id = mdc_param_in_machine.id
- mdc_technology_control_log.technology_control_setting_id = mdc_technology_control_setting.id
- hr_worker.hr_dept_id = hr_dept.id
- hr_time_sheet.hr_worker_id = hr_worker.id
"""


def get_tables_for_question(question: str) -> list:
    """
    Определить какие таблицы нужны для вопроса по ключевым словам.
    Возвращает список таблиц + связанные таблицы (авто-JOIN).
    """
    q_lower = question.lower()
    matched_tables = set()
    matched_keywords = []

    for keyword, tables in KEYWORD_TABLE_MAP.items():
        if keyword in q_lower:
            if tables:
                matched_tables.update(tables)
                matched_keywords.append(f'"{keyword}" → {tables}')
            # Если tables=None — это общий запрос, не добавляем таблицы

    # Автодобавление связанных таблиц
    expanded_tables = set(matched_tables)
    for table in list(matched_tables):
        if table in TABLE_DEPENDENCIES:
            expanded_tables.update(TABLE_DEPENDENCIES[table])

    return list(expanded_tables), matched_keywords


def build_dynamic_schema(tables: list) -> str:
    """
    Построить строку схемы только для указанных таблиц.
    """
    if not tables:
        return ""  # Полная схема будет использована как фоллбэк

    parts = []
    for table in sorted(tables):
        if table in TABLE_SCHEMAS:
            parts.append(TABLE_SCHEMAS[table])

    schema_str = "\n".join(parts)

    # Добавляем только релевантные связи
    relations_lines = []
    for line in ALL_RELATIONS.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        # Проверяем, есть ли хотя бы одна из наших таблиц в строке связи
        for table in tables:
            if table in line:
                relations_lines.append(line)
                break

    if relations_lines:
        schema_str += "\n\n" + "\n".join(relations_lines)

    return schema_str
