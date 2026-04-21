"""
Тестовые запросы для автоматической проверки ИИ-ассистента.
Фокус: MDC — оборудование.
SQL в формате, который генерирует LLM с системным промптом (алиасы таблиц + AS).
"""

TESTS = [
    # ===== УРОВЕНЬ 1: ПРОСТЫЕ =====
    {
        "question": "Какие станки есть на заводе?",
        "level": 1,
        "expected_sql": "SELECT m.name AS machine, m.num, m.oeeplan FROM mdc_machine m LIMIT 50",
    },
    {
        "question": "Какие подразделения (цеха) есть в системе MDC?",
        "level": 1,
        "expected_sql": "SELECT d.name FROM mdc_dept d LIMIT 50",
    },
    {
        "question": "Какие состояния станков есть в справочнике?",
        "level": 1,
        "expected_sql": "SELECT mp.name, mp.short_name, mp.code, mp.priority FROM mdc_machine_param mp LIMIT 50",
    },
    {
        "question": "Какие группы состояний станков существуют?",
        "level": 1,
        "expected_sql": "SELECT gp.name, gp.short_name, gp.plan_value FROM mdc_group_param gp LIMIT 50",
    },
    {
        "question": "Покажи историю состояний станков",
        "level": 1,
        "expected_sql": "SELECT m.name AS machine, mp.name AS state, mv.start_time, mv.end_time FROM mdc_monitoring_value_129 mv JOIN mdc_machine m ON mv.machine_id = m.id JOIN mdc_machine_param mp ON mv.machine_param_id = mp.id LIMIT 50",
    },
    {
        "question": "Какие программы выполнялись на станках?",
        "level": 1,
        "expected_sql": "SELECT m.name AS machine, l.name_up, l.dt_start, l.dt_end, l.processing_time FROM mdc_operating_program_execution_log l JOIN mdc_machine m ON l.machine_id = m.id LIMIT 50",
    },
    {
        "question": "Покажи расписание работы станков",
        "level": 1,
        "expected_sql": "SELECT m.name AS machine, sb.name, sb.week_day_num, sb.smena_num, sbi.time_from, sbi.time_to FROM mdc_shedule_base sb JOIN mdc_machine m ON sb.machine_id = m.id JOIN mdc_shedule_base_item sbi ON sb.id = sbi.shedule_base_id LIMIT 50",
    },
    {
        "question": "Покажи настройки контроля параметров на станках",
        "level": 1,
        "expected_sql": "SELECT tcs.name, tcs.group_param_id, tcs.machine_param_id FROM mdc_technology_control_setting tcs LIMIT 50",
    },
    {
        "question": "Покажи журнал нарушений контроля параметров",
        "level": 1,
        "expected_sql": "SELECT tcl.technology_control_setting_id, tcl.param_in_machine_id, tcl.param_value, tcl.dt_start, tcl.dt_end FROM mdc_technology_control_log tcl LIMIT 50",
    },
    {
        "question": "Покажи состояния станков, привязанные к группам",
        "level": 1,
        "expected_sql": "SELECT mpg.mdc_machine_param_id, mpg.mdc_group_param_id FROM mdc_machine_param_in_group mpg LIMIT 50",
    },

    # ===== УРОВЕНЬ 2: СРЕДНИЕ (JOIN) =====
    {
        "question": "Покажи станки с указанием их цеха",
        "level": 2,
        "expected_sql": "SELECT m.name, m.num, d.name AS dept_name FROM mdc_machine m JOIN mdc_dept d ON m.dept_id = d.id LIMIT 50",
    },
    {
        "question": "Кто и какие программы выполнял на станках?",
        "level": 2,
        "expected_sql": "SELECT m.name AS machine, w.surname, w.name, l.name_up, l.dt_start, l.processing_time FROM mdc_operating_program_execution_log l JOIN mdc_machine m ON l.machine_id = m.id JOIN hr_worker w ON l.worker_id = w.id LIMIT 50",
    },
    {
        "question": "Покажи детали, которые обрабатывались на станках",
        "level": 2,
        "expected_sql": "SELECT m.name AS machine, au.name AS detail_name, opa.name_up AS program_name FROM mdc_operating_program_assembly_unit opa JOIN mdc_machine m ON opa.machine_id = m.id JOIN tp_assembly_unit au ON opa.id_assembly_unit = au.id ORDER BY m.name, au.name",
    },
    {
        "question": "Покажи какие состояния отслеживаются на каждом станке",
        "level": 2,
        "expected_sql": "SELECT m.name AS machine, mp.name AS param_name FROM mdc_param_in_machine pim JOIN mdc_machine m ON pim.machine_id = m.id JOIN mdc_machine_param mp ON pim.machine_param_id = mp.id LIMIT 50",
    },
    {
        "question": "Покажи нарушения контроля с привязкой к станкам",
        "level": 2,
        "expected_sql": "SELECT m.name AS machine, tcs.name AS control_setting, tcl.param_value, tcl.dt_start, tcl.dt_end FROM mdc_technology_control_log tcl JOIN mdc_param_in_machine pim ON tcl.param_in_machine_id = pim.id JOIN mdc_machine m ON pim.machine_id = m.id JOIN mdc_technology_control_setting tcs ON tcl.technology_control_setting_id = tcs.id LIMIT 50",
    },
    {
        "question": "Покажи особые даты в расписании станков (праздники)",
        "level": 2,
        "expected_sql": "SELECT m.name AS machine, sm.shedule_date, sm.is_holiday FROM mdc_shedule_meta sm JOIN mdc_machine m ON sm.machine_id = m.id LIMIT 50",
    },
    {
        "question": "Покажи типы контроля параметров",
        "level": 2,
        "expected_sql": "SELECT tct.id, tct.technology_control_setting_id, tct.type_id, tct.is_tolerance, tct.is_emergency FROM mdc_technology_control_type tct LIMIT 50",
    },

    # ===== УРОВЕНЬ 3: СЛОЖНЫЕ (агрегации, GROUP BY) =====
    {
        "question": "Какое общее время простоев у каждого станка?",
        "level": 3,
        "expected_sql": "SELECT m.name AS machine, SUM(r.state_time) AS total_downtime_seconds FROM rep_monitoring_by_priority r JOIN mdc_machine m ON r.mdc_machineid = m.id JOIN mdc_machine_param mp ON r.mdc_machine_param_id = mp.id WHERE mp.id IN (SELECT mdc_machine_param_id FROM mdc_machine_param_in_group WHERE mdc_group_param_id IN (SELECT id FROM mdc_group_param WHERE name LIKE '%Простой%')) GROUP BY m.name",
    },
    {
        "question": "Сколько программ выполнено на каждом станке?",
        "level": 3,
        "expected_sql": "SELECT m.name AS machine, COUNT(l.id) AS program_count, SUM(l.processing_time) AS total_time FROM mdc_operating_program_execution_log l JOIN mdc_machine m ON l.machine_id = m.id GROUP BY m.name",
    },
    {
        "question": "Покажи аналитику по состояниям станков из rep_monitoring_by_priority",
        "level": 3,
        "expected_sql": "SELECT m.name AS machine, mp.name AS state_name, r.from_date, r.to_date, r.state_time, r.shift_num FROM rep_monitoring_by_priority r JOIN mdc_machine m ON r.mdc_machineid = m.id JOIN mdc_machine_param mp ON r.mdc_machine_param_id = mp.id LIMIT 50",
    },
    {
        "question": "Какие программы привязаны к каким сборочным единицам на каждом станке?",
        "level": 3,
        "expected_sql": "SELECT m.name AS machine, opa.name_up, au.name AS assembly_unit FROM mdc_operating_program_assembly_unit opa JOIN mdc_machine m ON opa.machine_id = m.id JOIN tp_assembly_unit au ON opa.id_assembly_unit = au.id LIMIT 50",
    },
    {
        "question": "Покажи настройки контроля с привязкой к группам состояний и параметрам",
        "level": 3,
        "expected_sql": "SELECT tcs.name, gp.name AS group_name, mp.name AS param_name FROM mdc_technology_control_setting tcs JOIN mdc_group_param gp ON tcs.group_param_id = gp.id JOIN mdc_machine_param mp ON tcs.machine_param_id = mp.id LIMIT 50",
    },
    {
        "question": "Покажи станки у которых плановый OEE больше нуля",
        "level": 3,
        "expected_sql": "SELECT m.name, m.num, m.oeeplan FROM mdc_machine m WHERE m.oeeplan > 0 LIMIT 50",
    },

    # ===== УРОВЕНЬ 4: ОЧЕНЬ СЛОЖНЫЕ =====
    {
        "question": "Покажи полную информацию о работе каждого станка: цех, программы, оператор",
        "level": 4,
        "expected_sql": "SELECT m.name AS machine, m.num, d.name AS dept_name, l.name_up AS last_program, l.dt_start AS program_start, l.processing_time, w.surname AS worker_surname, w.name AS worker_name, w.prof_name FROM mdc_machine m LEFT JOIN mdc_dept d ON m.dept_id = d.id LEFT JOIN mdc_operating_program_execution_log l ON m.id = l.machine_id LEFT JOIN hr_worker w ON l.worker_id = w.id ORDER BY m.name",
    },
    {
        "question": "Сравни загрузку и простой станков по каждому цеху",
        "level": 4,
        "expected_sql": "SELECT d.name AS dept_name, r.mdc_machine_load_time AS load_time, r.mdc_machine_break_time AS break_time, r.mdc_machine_fund AS fund_time, ROUND(r.mdc_machine_load_time * 100.0 / r.mdc_machine_fund, 2) AS load_percent FROM rep_main_analitic r JOIN hr_dept d ON r.dept_num = d.root_num WHERE r.mdc_machine_fund > 0 ORDER BY load_percent DESC",
    },
    {
        "question": "Какие станки имели наибольший простой в последний месяц?",
        "level": 4,
        "expected_sql": "SELECT m.name AS machine, mp.name AS state_name, SUM(r.state_time) AS total_seconds FROM rep_monitoring_by_priority r JOIN mdc_machine m ON r.mdc_machineid = m.id JOIN mdc_machine_param mp ON r.mdc_machine_param_id = mp.id WHERE r.from_date >= date('now', '-1 month') GROUP BY m.name, mp.name ORDER BY total_seconds DESC LIMIT 10",
    },
    {
        "question": "Покажи состояния станков с группировкой по группам состояний",
        "level": 4,
        "expected_sql": "SELECT gp.name AS group_name, mp.name AS param_name, COUNT(*) AS count FROM mdc_machine_param_in_group mpg JOIN mdc_group_param gp ON mpg.mdc_group_param_id = gp.id JOIN mdc_machine_param mp ON mpg.mdc_machine_param_id = mp.id GROUP BY gp.name, mp.name",
    },
    {
        "question": "Покажи расписание станков с временными интервалами и привязкой к цехам",
        "level": 4,
        "expected_sql": "SELECT m.name AS machine, d.name AS dept_name, sb.name AS schedule_name, sb.week_day_num, sb.smena_num, sbi.time_from, sbi.time_to FROM mdc_shedule_base sb JOIN mdc_machine m ON sb.machine_id = m.id JOIN mdc_dept d ON sb.dept_id = d.id JOIN mdc_shedule_base_item sbi ON sb.id = sbi.shedule_base_id ORDER BY m.name, sb.week_day_num",
    },
    {
        "question": "Покажи все нарушения контроля с названиями станков и настройками",
        "level": 4,
        "expected_sql": "SELECT m.name AS machine, tcs.name AS setting_name, tcl.param_value, tcl.dt_start, tcl.dt_end FROM mdc_technology_control_log tcl JOIN mdc_param_in_machine pim ON tcl.param_in_machine_id = pim.id JOIN mdc_machine m ON pim.machine_id = m.id JOIN mdc_technology_control_setting tcs ON tcl.technology_control_setting_id = tcs.id ORDER BY tcl.dt_start DESC",
    },
]
