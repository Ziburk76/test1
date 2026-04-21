"""
Скрипт генерации реалистичных демо-данных для производственной БД.
Заменить database.db перед запуском.
"""
import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

random.seed(42)


def create_connection():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def create_tables(conn):
    cursor = conn.cursor()

    # === MDC: Подразделения ===
    cursor.execute("""
        CREATE TABLE mdc_dept (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255),
            parent_id INTEGER,
            integration_id VARCHAR(255)
        )
    """)

    # === MDC: Группы состояний ===
    cursor.execute("""
        CREATE TABLE mdc_group_param (
            id INTEGER PRIMARY KEY,
            name VARCHAR(200),
            parent_id INTEGER,
            short_name VARCHAR(255),
            color INTEGER,
            plan_value NUMERIC(18,2)
        )
    """)

    # === MDC: Станки ===
    cursor.execute("""
        CREATE TABLE mdc_machine (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255),
            short_name VARCHAR(50),
            num VARCHAR(50),
            dept_id INTEGER,
            _root_num INTEGER,
            _root_num_x INTEGER,
            integration_id VARCHAR(255),
            dt_commissioning TIMESTAMP,
            dt_decommissioning TIMESTAMP,
            oeeplan NUMERIC(18,2)
        )
    """)

    # === MDC: Состояния ===
    cursor.execute("""
        CREATE TABLE mdc_machine_param (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255),
            short_name VARCHAR(255),
            parent_id INTEGER,
            priority INTEGER,
            code INTEGER,
            is_service_state INTEGER,
            is_by_shedule INTEGER
        )
    """)

    # === MDC: Состояния в группах ===
    cursor.execute("""
        CREATE TABLE mdc_machine_param_in_group (
            id INTEGER PRIMARY KEY,
            mdc_machine_param_id INTEGER,
            mdc_group_param_id INTEGER
        )
    """)

    # === MDC: Параметры на станке ===
    cursor.execute("""
        CREATE TABLE mdc_param_in_machine (
            id INTEGER PRIMARY KEY,
            machine_id INTEGER,
            machine_param_id INTEGER
        )
    """)

    # === MDC: История состояний (129) ===
    cursor.execute("""
        CREATE TABLE mdc_monitoring_value_129 (
            id INTEGER PRIMARY KEY,
            machine_id INTEGER,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            param_in_machine_id INTEGER,
            machine_param_id INTEGER
        )
    """)

    # === MDC: Лог выполнения программ ===
    cursor.execute("""
        CREATE TABLE mdc_operating_program_execution_log (
            id INTEGER PRIMARY KEY,
            machine_id INTEGER,
            worker_id INTEGER,
            name_up VARCHAR(255),
            dt_start TIMESTAMP,
            dt_end TIMESTAMP,
            processing_time NUMERIC(18,2)
        )
    """)

    # === MDC: Программа → деталь ===
    cursor.execute("""
        CREATE TABLE mdc_operating_program_assembly_unit (
            id INTEGER PRIMARY KEY,
            machine_id INTEGER,
            name_up VARCHAR(255),
            id_assembly_unit INTEGER
        )
    """)

    # === MDC: Расписание базовое ===
    cursor.execute("""
        CREATE TABLE mdc_shedule_base (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255),
            week_day_num INTEGER,
            smena_num INTEGER,
            dept_id INTEGER,
            machine_id INTEGER,
            shedule_meta_id INTEGER
        )
    """)

    # === MDC: Расписание — интервалы ===
    cursor.execute("""
        CREATE TABLE mdc_shedule_base_item (
            id INTEGER PRIMARY KEY,
            shedule_base_id INTEGER,
            time_from TIME,
            time_to TIME
        )
    """)

    # === MDC: Мета расписания ===
    cursor.execute("""
        CREATE TABLE mdc_shedule_meta (
            id INTEGER PRIMARY KEY,
            is_holiday INTEGER,
            shedule_date TIMESTAMP,
            dept_id INTEGER,
            machine_id INTEGER,
            shedule_type_id INTEGER
        )
    """)

    # === MDC: Настройки контроля ===
    cursor.execute("""
        CREATE TABLE mdc_technology_control_setting (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255),
            group_param_id INTEGER,
            machine_param_id INTEGER
        )
    """)

    # === MDC: Журнал нарушений ===
    cursor.execute("""
        CREATE TABLE mdc_technology_control_log (
            id INTEGER PRIMARY KEY,
            technology_control_setting_id INTEGER,
            param_in_machine_id INTEGER,
            param_value NUMERIC(18,2),
            dt_start TIMESTAMP,
            dt_end TIMESTAMP,
            technology_operation_id INTEGER
        )
    """)

    # === MDC: Типы контроля ===
    cursor.execute("""
        CREATE TABLE mdc_technology_control_type (
            id INTEGER PRIMARY KEY,
            technology_control_setting_id INTEGER,
            type_id INTEGER,
            is_tolerance INTEGER,
            is_emergency INTEGER
        )
    """)

    # === HR: Подразделения ===
    cursor.execute("""
        CREATE TABLE hr_dept (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255),
            parent_id INTEGER,
            root_num INTEGER,
            integration_id VARCHAR(255)
        )
    """)

    # === HR: Должности ===
    cursor.execute("""
        CREATE TABLE hr_work_position (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255)
        )
    """)

    # === HR: Сотрудники ===
    cursor.execute("""
        CREATE TABLE hr_worker (
            id INTEGER PRIMARY KEY,
            surname VARCHAR(50),
            name VARCHAR(50),
            patronymic VARCHAR(50),
            personal_num VARCHAR(50),
            smart_card_code INTEGER,
            hr_dept_id INTEGER,
            dept_num INTEGER,
            prof_name VARCHAR(255),
            dt_accept TIMESTAMP,
            dt_fired TIMESTAMP,
            is_deleted INTEGER
        )
    """)

    # === HR: Типы трудозатрат ===
    cursor.execute("""
        CREATE TABLE hr_time_sheet_type (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255)
        )
    """)

    # === HR: Трудозатраты ===
    cursor.execute("""
        CREATE TABLE hr_time_sheet (
            id INTEGER PRIMARY KEY,
            dt_day TIMESTAMP,
            hr_worker_id INTEGER,
            hr_time_sheet_type_id INTEGER,
            time NUMERIC(5,2)
        )
    """)

    # === HR: Кадровые перемещения ===
    cursor.execute("""
        CREATE TABLE hr_transfers_personnel (
            id INTEGER PRIMARY KEY,
            unique_code INTEGER,
            hr_dept_id INTEGER,
            dept_num INTEGER,
            tab_num INTEGER,
            dt_accept TIMESTAMP,
            dt_fired TIMESTAMP,
            is_type INTEGER
        )
    """)

    # === HR: Увольнения по цехам ===
    cursor.execute("""
        CREATE TABLE hr_worker_fired_dept (
            id INTEGER PRIMARY KEY,
            dt_day TIMESTAMP,
            dept_num INTEGER,
            begin_month_num INTEGER,
            worker_fired_num INTEGER,
            average_headcount_perscent REAL
        )
    """)

    # === REP: Мониторинг по приоритетам ===
    cursor.execute("""
        CREATE TABLE rep_monitoring_by_priority (
            id INTEGER PRIMARY KEY,
            mdc_machineid INTEGER,
            mdc_machine_param_id INTEGER,
            from_date TIMESTAMP,
            to_date TIMESTAMP,
            state_time INTEGER,
            shift_num INTEGER,
            dt_calc TIMESTAMP,
            tp_technology_operation_id INTEGER
        )
    """)

    # === REP: Сводная аналитика ===
    cursor.execute("""
        CREATE TABLE rep_main_analitic (
            id INTEGER PRIMARY KEY,
            dept_num INTEGER,
            dt_of_month TIMESTAMP,
            hr_fund_time NUMERIC(18,4),
            hr_lose_time NUMERIC(18,4),
            hr_people_count NUMERIC(18,4),
            mdc_machine_load_time NUMERIC(18,4),
            mdc_machine_break_time NUMERIC(18,4),
            mdc_machine_fund NUMERIC(18,4),
            mdc_machine_fund_24 NUMERIC(18,4),
            qa_defective_part_count NUMERIC(18,4),
            staff_turnover NUMERIC(12,5),
            hr_worker_count INTEGER,
            hr_people_count_plan INTEGER
        )
    """)

    # === REP: Дневная аналитика ===
    cursor.execute("""
        CREATE TABLE rep_daily_worker_analytic (
            id INTEGER PRIMARY KEY,
            dt_day DATE,
            hr_worker_id INTEGER,
            hr_work_position_id INTEGER,
            dept_num INTEGER,
            work_time NUMERIC,
            manufactured_parts_log_count BIGINT,
            manufactured_parts_log_plan_time NUMERIC,
            manufactured_parts_log_fact_time NUMERIC,
            downtime NUMERIC,
            fond NUMERIC,
            status VARCHAR(255)
        )
    """)

    # === TP: Сборочные единицы ===
    cursor.execute("""
        CREATE TABLE tp_assembly_unit (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255)
        )
    """)

    # === TP: Технологические операции ===
    cursor.execute("""
        CREATE TABLE tp_technology_operation (
            id INTEGER PRIMARY KEY,
            code VARCHAR(30),
            description TEXT,
            machine_time INTEGER,
            piece_time NUMERIC(18,5)
        )
    """)

    conn.commit()


def fill_data(conn):
    cursor = conn.cursor()
    now = datetime.now()

    # ========== MDC: Цеха ==========
    depts = [
        (1, 'Цех №5 — Механообрабатывающий', None, 'MDC_DEPT_5'),
        (2, 'Цех №12 — Сборочный', None, 'MDC_DEPT_12'),
        (3, 'Цех №32 — Термический', None, 'MDC_DEPT_32'),
        (4, 'Участок 5.1 — Токарный', 1, 'MDC_DEPT_5_1'),
        (5, 'Участок 5.2 — Фрезерный', 1, 'MDC_DEPT_5_2'),
        (6, 'Участок 12.1 — Сборка узлов', 2, 'MDC_DEPT_12_1'),
    ]
    cursor.executemany("INSERT INTO mdc_dept VALUES (?,?,?,?)", depts)

    # ========== MDC: Группы состояний ==========
    groups = [
        (1, 'Производство', None, 'Пр-во', 0x00AA00, 85.00),
        (2, 'Простой', None, 'Простой', 0xFF0000, 5.00),
        (3, 'Наладка', None, 'Наладка', 0xFFAA00, 8.00),
        (4, 'Ремонт', None, 'Ремонт', 0xAA00AA, 2.00),
    ]
    cursor.executemany("INSERT INTO mdc_group_param VALUES (?,?,?,?,?,?)", groups)

    # ========== MDC: Состояния ==========
    params = [
        (1, 'Работа', 'Работа', None, 1, 1, 0, 1),
        (2, 'Простой — нет задания', 'Нет задания', None, 2, 10, 0, 0),
        (3, 'Простой — ожидание инструмента', 'Ож. инструмент', None, 3, 11, 0, 0),
        (4, 'Простой — поломка', 'Поломка', None, 1, 12, 0, 0),
        (5, 'Простой — обед', 'Обед', None, 4, 13, 1, 1),
        (6, 'Наладка — переналадка', 'Переналадка', None, 5, 20, 0, 0),
        (7, 'Наладка — настройка', 'Настройка', None, 6, 21, 0, 0),
        (8, 'Ремонт — плановый', 'План. ремонт', None, 7, 30, 0, 0),
        (9, 'Ремонт — аварийный', 'Авар. ремонт', None, 1, 31, 0, 0),
        (10, 'Производство — выполнение УП', 'Вып. УП', None, 1, 2, 0, 1),
    ]
    cursor.executemany("INSERT INTO mdc_machine_param VALUES (?,?,?,?,?,?,?,?)", params)

    # ========== MDC: Состояния → Группы ==========
    param_in_group = [
        (1, 1, 1),   # Работа → Производство
        (2, 10, 1),  # Вып. УП → Производство
        (3, 2, 2),   # Нет задания → Простой
        (4, 3, 2),   # Ож. инструмент → Простой
        (5, 4, 2),   # Поломка → Простой
        (6, 5, 2),   # Обед → Простой
        (7, 6, 3),   # Переналадка → Наладка
        (8, 7, 3),   # Настройка → Наладка
        (9, 8, 4),   # План. ремонт → Ремонт
        (10, 9, 4),  # Авар. ремонт → Ремонт
    ]
    cursor.executemany("INSERT INTO mdc_machine_param_in_group VALUES (?,?,?)", param_in_group)

    # ========== MDC: Станки ==========
    machines = [
        (1, 'ЗУБ-9074 Лазерный станок, модели SAMSUNG LCV-2586', 'ЗУБ-9074', 'ЗУБ-9074', 1, 5, 5, 'INT_ZUB_9074',
         datetime(2020, 3, 15), None, 82.50),
        (2, 'ШЛФ-1414 Токарный станок, модели DMG MORI NLX-3499', 'ШЛФ-1414', 'ШЛФ-1414', 1, 5, 5, 'INT_SHLF_1414',
         datetime(2019, 7, 20), None, 78.00),
        (3, 'СВР-8274 Токарно-карусельный станок, модели DMG MORI NLX-9075', 'СВР-8274', 'СВР-8274', 1, 5, 5, 'INT_SVR_8274',
         datetime(2021, 1, 10), None, 75.00),
        (4, 'ФР-2201 Фрезерный обрабатывающий центр, HAAS VF-2', 'ФР-2201', 'ФР-2201', 2, 5, 5, 'INT_FR_2201',
         datetime(2018, 11, 5), None, 80.00),
        (5, 'ШЛ-3305 Шлифовальный станок, Studer S41', 'ШЛ-3305', 'ШЛ-3305', 2, 5, 5, 'INT_SHL_3305',
         datetime(2022, 6, 1), None, 85.00),
        (6, 'ЗУБ-1102 Зубофрезерный станок, Liebherr LC 120', 'ЗУБ-1102', 'ЗУБ-1102', 4, 12, 12, 'INT_ZUB_1102',
         datetime(2017, 4, 22), None, 70.00),
        (7, 'РД-4401 Расточной станок, TOS WHN 13', 'РД-4401', 'РД-4401', 4, 12, 12, 'INT_RD_4401',
         datetime(2016, 9, 15), None, 65.00),
        (8, 'ПР-5501 Пресс гидравлический, SCHULER MSP 500', 'ПР-5501', 'ПР-5501', 5, 32, 32, 'INT_PR_5501',
         datetime(2023, 2, 28), None, 90.00),
        (9, 'ТМ-6603 Термопечь, Nabertherm N 120/11', 'ТМ-6603', 'ТМ-6603', 5, 32, 32, 'INT_TM_6603',
         datetime(2019, 12, 10), None, 88.00),
        (10, 'КР-7701 Круглошлифовальный, Junker Quickpoint', 'КР-7701', 'КР-7701', 3, 32, 32, 'INT_KR_7701',
         datetime(2020, 8, 5), None, 72.00),
        (11, 'ГН-8801 Гибочный станок, TRUMPF TruBend 5230', 'ГН-8801', 'ГН-8801', 3, 32, 32, 'INT_GN_8801',
         datetime(2021, 5, 18), None, 83.00),
        (12, 'ЛАЗ-9902 Лазерная резка, Trumpf TruLaser 3030', 'ЛАЗ-9902', 'ЛАЗ-9902', 6, 12, 12, 'INT_LAZ_9902',
         datetime(2024, 1, 15), None, 92.00),
    ]
    cursor.executemany("INSERT INTO mdc_machine VALUES (?,?,?,?,?,?,?,?,?,?,?)", machines)

    # ========== MDC: Параметры на станках (какие состояния отслеживаются) ==========
    param_in_machine = []
    pid = 1
    for mid in range(1, 13):
        for param_id in [1, 2, 3, 4, 5, 6, 8, 10]:
            param_in_machine.append((pid, mid, param_id))
            pid += 1
    cursor.executemany("INSERT INTO mdc_param_in_machine VALUES (?,?,?)", param_in_machine)

    # ========== MDC: История состояний (129) ==========
    monitoring = []
    mid = 1
    param_names = {1: 'Работа', 2: 'Нет задания', 3: 'Ож. инструмент', 4: 'Поломка', 5: 'Обед', 6: 'Переналадка', 8: 'План. ремонт', 10: 'Вып. УП'}

    for machine_id in range(1, 13):
        # Генерируем историю за последние 3 месяца
        current_time = now - timedelta(days=90)
        end_time_limit = now
        while current_time < end_time_limit:
            # Рабочее время: 8:00-20:00
            if 8 <= current_time.hour < 20 and current_time.weekday() < 5:
                # Определяем состояние
                r = random.random()
                if r < 0.55:
                    param_id = 10  # Вып. УП
                    duration = random.randint(30, 180)
                elif r < 0.70:
                    param_id = 1  # Работа
                    duration = random.randint(60, 240)
                elif r < 0.80:
                    param_id = 6  # Переналадка
                    duration = random.randint(15, 45)
                elif r < 0.88:
                    param_id = 5  # Обед
                    duration = random.randint(30, 60)
                elif r < 0.93:
                    param_id = 2  # Нет задания
                    duration = random.randint(10, 40)
                elif r < 0.97:
                    param_id = 3  # Ож. инструмент
                    duration = random.randint(10, 30)
                else:
                    param_id = 4  # Поломка
                    duration = random.randint(20, 120)

                start = current_time
                end = start + timedelta(minutes=duration)
                if end > end_time_limit:
                    end = end_time_limit

                monitoring.append((mid, machine_id, start.strftime('%Y-%m-%d %H:%M:%S'),
                                   end.strftime('%Y-%m-%d %H:%M:%S'), mid, param_id))
                mid += 1
                current_time = end
            else:
                current_time += timedelta(hours=1)

    cursor.executemany("INSERT INTO mdc_monitoring_value_129 VALUES (?,?,?,?,?,?)", monitoring)

    # ========== TP: Сборочные единицы (детали) ==========
    assembly_units = [
        (1, 'Корпус редуктора Р-250'),
        (2, 'Вал приводной ВП-12'),
        (3, 'Шестерня коническая ШК-45'),
        (4, 'Фланец соединительный ФС-80'),
        (5, 'Крышка подшипника КП-30'),
        (6, 'Кольцо уплотнительное КУ-15'),
        (7, 'Ось опорная АО-22'),
        (8, 'Стойка крепежная СК-10'),
        (9, 'Втулка направляющая ВН-18'),
        (10, 'Диск тормозной ДТ-55'),
    ]
    cursor.executemany("INSERT INTO tp_assembly_unit VALUES (?,?)", assembly_units)

    # ========== TP: Технологические операции ==========
    tech_operations = [
        (1, 'TO-001', 'Токарная черновая обработка корпуса', 120, 45.50000),
        (2, 'TO-002', 'Токарная чистовая обработка корпуса', 90, 35.20000),
        (3, 'TO-003', 'Фрезерная обработка плоскостей', 75, 28.80000),
        (4, 'TO-004', 'Сверление отверстий Ø12-Ø25', 45, 15.60000),
        (5, 'TO-005', 'Шлифование наружных поверхностей', 60, 22.40000),
        (6, 'TO-006', 'Зубонарезка модуль 2.5', 90, 38.10000),
        (7, 'TO-007', 'Термообработка — закалка HRC 58-62', 180, 0.00000),
        (8, 'TO-008', 'Шлифование внутреннее', 55, 20.30000),
        (9, 'TO-009', 'Контроль размеров и допусков', 30, 12.50000),
        (10, 'TO-010', 'Сборка узла редуктора', 240, 0.00000),
    ]
    cursor.executemany("INSERT INTO tp_technology_operation VALUES (?,?,?,?,?)", tech_operations)

    # ========== HR: Подразделения ==========
    hr_depts = [
        (1, 'Цех №5 — Механообрабатывающий', None, 5, 'HR_DEPT_5'),
        (2, 'Цех №12 — Сборочный', None, 12, 'HR_DEPT_12'),
        (3, 'Цех №32 — Термический', None, 32, 'HR_DEPT_32'),
        (4, 'Участок 5.1 — Токарный', 1, 5, 'HR_DEPT_5_1'),
        (5, 'Участок 5.2 — Фрезерный', 1, 5, 'HR_DEPT_5_2'),
        (6, 'Участок 12.1 — Сборка узлов', 2, 12, 'HR_DEPT_12_1'),
    ]
    cursor.executemany("INSERT INTO hr_dept VALUES (?,?,?,?,?)", hr_depts)

    # ========== HR: Должности ==========
    positions = [
        (1, 'Оператор станков с ЧПУ'),
        (2, 'Наладчик станков'),
        (3, 'Слесарь-сборщик'),
        (4, 'Мастер участка'),
        (5, 'Инженер-технолог'),
        (6, 'Контролёр ОТК'),
        (7, 'Термист'),
        (8, 'Шлифовщик'),
    ]
    cursor.executemany("INSERT INTO hr_work_position VALUES (?,?)", positions)

    # ========== HR: Сотрудники ==========
    surnames_m = ['Иванов', 'Петров', 'Сидоров', 'Козлов', 'Новиков', 'Морозов', 'Волков', 'Соколов',
                  'Лебедев', 'Кузнецов', 'Попов', 'Семёнов', 'Голубев', 'Виноградов', 'Богданов',
                  'Фёдоров', 'Орлов', 'Андреев', 'Макаров', 'Никитин']
    surnames_f = ['Иванова', 'Петрова', 'Сидорова', 'Козлова', 'Новикова', 'Морозова', 'Волкова', 'Соколова']
    names_m = ['Александр', 'Дмитрий', 'Максим', 'Сергей', 'Андрей', 'Алексей', 'Артём', 'Илья', 'Кирилл', 'Михаил']
    names_f = ['Елена', 'Ольга', 'Наталья', 'Мария', 'Анна', 'Татьяна', 'Ирина', 'Светлана']
    patronymics_m = ['Александрович', 'Дмитриевич', 'Сергеевич', 'Андреевич', 'Иванович', 'Петрович', 'Николаевич']
    patronymics_f = ['Александровна', 'Дмитриевна', 'Сергеевна', 'Андреевна', 'Ивановна', 'Петровна']

    workers = []
    transfers = []
    tid = 1

    # Активные сотрудники — 40 человек
    for i in range(1, 41):
        wid = i
        dept_id = random.choice([1, 2, 3, 4, 5, 6])
        dept_num = {1: 5, 2: 12, 3: 32, 4: 5, 5: 5, 6: 12}[dept_id]
        is_male = i <= 35

        if is_male:
            surname = random.choice(surnames_m)
            name = random.choice(names_m)
            patronymic = random.choice(patronymics_m)
        else:
            surname = random.choice(surnames_f)
            name = random.choice(names_f)
            patronymic = random.choice(patronymics_f)

        prof = random.choice(['Оператор станков с ЧПУ', 'Наладчик станков', 'Слесарь-сборщик',
                              'Шлифовщик', 'Термист', 'Мастер участка', 'Инженер-технолог'])

        accept_date = datetime(2020, random.randint(1, 12), random.randint(1, 28))

        workers.append((wid, surname, name, patronymic, f'TN-{wid:04d}', 100000 + wid,
                        dept_id, dept_num, prof, accept_date.strftime('%Y-%m-%d %H:%M:%S'), None, 0))

        transfers.append((tid, 100000 + wid, dept_id, dept_num, wid,
                          accept_date.strftime('%Y-%m-%d %H:%M:%S'), None, 0))
        tid += 1

    # Уволенные — 5 человек
    for i in range(41, 46):
        wid = i
        surname = random.choice(surnames_m)
        name = random.choice(names_m)
        patronymic = random.choice(patronymics_m)
        dept_id = random.choice([1, 2, 3])
        dept_num = {1: 5, 2: 12, 3: 32}[dept_id]
        prof = random.choice(['Оператор станков с ЧПУ', 'Слесарь-сборщик', 'Наладчик станков'])
        accept_date = datetime(2019, random.randint(1, 12), random.randint(1, 28))
        fired_date = datetime(2025, random.randint(6, 12), random.randint(1, 28))

        workers.append((wid, surname, name, patronymic, f'TN-{wid:04d}', 100000 + wid,
                        dept_id, dept_num, prof, accept_date.strftime('%Y-%m-%d %H:%M:%S'),
                        fired_date.strftime('%Y-%m-%d %H:%M:%S'), 1))

        transfers.append((tid, 100000 + wid, dept_id, dept_num, wid,
                          accept_date.strftime('%Y-%m-%d %H:%M:%S'),
                          fired_date.strftime('%Y-%m-%d %H:%M:%S'), 1))
        tid += 1

    cursor.executemany("INSERT INTO hr_worker VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", workers)
    cursor.executemany("INSERT INTO hr_transfers_personnel VALUES (?,?,?,?,?,?,?,?)", transfers)

    # ========== HR: Типы трудозатрат ==========
    ts_types = [
        (1, 'Рабочее время'),
        (2, 'Ночные часы'),
        (3, 'Сверхурочные'),
        (4, 'Простой'),
        (5, 'Отпуск'),
    ]
    cursor.executemany("INSERT INTO hr_time_sheet_type VALUES (?,?)", ts_types)

    # ========== HR: Трудозатраты (30 дней × 40 чел) ==========
    time_sheets = []
    tsid = 1
    for day_offset in range(30):
        day = now - timedelta(days=day_offset)
        if day.weekday() >= 5:
            continue
        for wid in range(1, 41):
            hours = round(random.uniform(7.0, 10.0), 2)
            time_sheets.append((tsid, day.strftime('%Y-%m-%d'), wid, 1, hours))
            tsid += 1
            # Иногда ночные / сверхурочные
            if random.random() < 0.15:
                night_hours = round(random.uniform(1.0, 3.0), 2)
                time_sheets.append((tsid, day.strftime('%Y-%m-%d'), wid, 2, night_hours))
                tsid += 1
            if random.random() < 0.1:
                overtime = round(random.uniform(1.0, 4.0), 2)
                time_sheets.append((tsid, day.strftime('%Y-%m-%d'), wid, 3, overtime))
                tsid += 1

    cursor.executemany("INSERT INTO hr_time_sheet VALUES (?,?,?,?,?)", time_sheets)

    # ========== HR: Увольнения по цехам (за 6 месяцев) ==========
    fired_stats = []
    fsid = 1
    for month_offset in range(6):
        month_start = datetime(now.year, now.month, 1) - timedelta(days=30 * month_offset)
        for dept_num in [5, 12, 32]:
            begin_count = random.randint(12, 18)
            fired_count = random.randint(0, 2)
            turnover = round(fired_count / begin_count * 100, 2) if begin_count > 0 else 0
            fired_stats.append((fsid, month_start.strftime('%Y-%m-%d'), dept_num,
                                begin_count, fired_count, turnover))
            fsid += 1

    cursor.executemany("INSERT INTO hr_worker_fired_dept VALUES (?,?,?,?,?,?)", fired_stats)

    # ========== MDC: Лог выполнения программ ==========
    program_names = [
        'PROG_KORPUS_R250_OP10.NC', 'PROG_VAL_VP12_OP20.NC', 'PROG_SHEST_SHK45_OP30.NC',
        'PROG_FLANETS_FS80_OP10.NC', 'PROG_KRYSHKA_KP30_OP40.NC', 'PROG_OS_AO22_OP10.NC',
        'PROG_DISK_DT55_OP50.NC', 'PROG_STOYKA_SK10_OP20.NC', 'PROG_VTULKA_VN18_OP30.NC',
        'PROG_KOLTSEO_KU15_OP10.NC',
    ]

    exec_logs = []
    elog_id = 1
    for machine_id in range(1, 13):
        # 2-5 программ на станок
        num_programs = random.randint(2, 5)
        for _ in range(num_programs):
            worker_id = random.randint(1, 40)
            prog_name = random.choice(program_names)
            dt_start = now - timedelta(days=random.randint(1, 60), hours=random.randint(0, 12),
                                       minutes=random.randint(0, 59))
            proc_time = round(random.uniform(0.5, 6.0), 2)
            dt_end = dt_start + timedelta(hours=proc_time)

            exec_logs.append((elog_id, machine_id, worker_id, prog_name,
                              dt_start.strftime('%Y-%m-%d %H:%M:%S'),
                              dt_end.strftime('%Y-%m-%d %H:%M:%S'), proc_time))
            elog_id += 1

    cursor.executemany("INSERT INTO mdc_operating_program_execution_log VALUES (?,?,?,?,?,?,?)", exec_logs)

    # ========== MDC: Программа → деталь ==========
    prog_assembly = []
    paid = 1
    for log in exec_logs:
        machine_id = log[1]
        prog_name = log[3]
        assembly_id = random.randint(1, 10)
        prog_assembly.append((paid, machine_id, prog_name, assembly_id))
        paid += 1

    cursor.executemany("INSERT INTO mdc_operating_program_assembly_unit VALUES (?,?,?,?)", prog_assembly)

    # ========== MDC: Расписание базовое ==========
    schedules = []
    sched_id = 1
    for machine_id in range(1, 13):
        dept_id = machines[machine_id - 1][4]  # dept_id из списка станков
        # Пн-Пт, 1 смена
        for day_num in range(1, 6):
            schedules.append((sched_id, f'Расписание станка {machine_id} — ПН',
                              day_num, 1, dept_id, machine_id, None))
            sched_id += 1

    cursor.executemany("INSERT INTO mdc_shedule_base VALUES (?,?,?,?,?,?,?)", schedules)

    # ========== MDC: Расписание — интервалы ==========
    schedule_items = []
    siid = 1
    for s in schedules:
        # 8:00-12:00, 13:00-17:00
        schedule_items.append((siid, s[0], '08:00:00', '12:00:00'))
        siid += 1
        schedule_items.append((siid, s[0], '13:00:00', '17:00:00'))
        siid += 1

    cursor.executemany("INSERT INTO mdc_shedule_base_item VALUES (?,?,?,?)", schedule_items)

    # ========== MDC: Мета расписания (праздники) ==========
    holidays = [
        (1, 1, '2025-01-01', None, None, 1),
        (2, 1, '2025-01-07', None, None, 1),
        (3, 1, '2025-02-23', None, None, 1),
        (4, 1, '2025-03-08', None, None, 1),
        (5, 1, '2025-05-01', None, None, 1),
        (6, 1, '2025-05-09', None, None, 1),
        (7, 1, '2025-06-12', None, None, 1),
        (8, 1, '2025-11-04', None, None, 1),
    ]
    cursor.executemany("INSERT INTO mdc_shedule_meta VALUES (?,?,?,?,?,?)", holidays)

    # ========== MDC: Настройки контроля ==========
    control_settings = [
        (1, 'Контроль температуры шпинделя', 1, 1),
        (2, 'Контроль вибрации', 2, 1),
        (3, 'Контроль температуры печи', 1, 9),
        (4, 'Контроль усилия пресса', 4, 8),
        (5, 'Контроль скорости подачи', 3, 1),
        (6, 'Контроль давления СОЖ', 2, 2),
    ]
    cursor.executemany("INSERT INTO mdc_technology_control_setting VALUES (?,?,?,?)", control_settings)

    # ========== MDC: Типы контроля ==========
    control_types = [
        (1, 1, 1, 1, 0),
        (2, 1, 2, 0, 0),
        (3, 2, 1, 0, 1),
        (4, 3, 1, 1, 0),
        (5, 3, 2, 0, 1),
        (6, 4, 1, 1, 0),
    ]
    cursor.executemany("INSERT INTO mdc_technology_control_type VALUES (?,?,?,?,?)", control_types)

    # ========== MDC: Журнал нарушений ==========
    violations = []
    vid = 1
    for _ in range(20):
        setting_id = random.randint(1, 6)
        param_in_m_id = random.randint(1, len(param_in_machine))
        param_value = round(random.uniform(20.0, 150.0), 2)
        dt_start = now - timedelta(days=random.randint(1, 90), hours=random.randint(0, 23))
        dt_end = dt_start + timedelta(minutes=random.randint(5, 60))
        tech_op_id = random.randint(1, 10)

        violations.append((vid, setting_id, param_in_m_id, param_value,
                           dt_start.strftime('%Y-%m-%d %H:%M:%S'),
                           dt_end.strftime('%Y-%m-%d %H:%M:%S'), tech_op_id))
        vid += 1

    cursor.executemany("INSERT INTO mdc_technology_control_log VALUES (?,?,?,?,?,?,?)", violations)

    # ========== REP: Мониторинг по приоритетам ==========
    monitoring_rep = []
    mrid = 1
    for machine_id in range(1, 13):
        for month_offset in range(3):
            from_date = now - timedelta(days=30 * (month_offset + 1))
            to_date = now - timedelta(days=30 * month_offset)
            for param_id in [1, 2, 4, 6, 10]:
                state_time = random.randint(3600, 86400)  # секунды
                shift = random.randint(1, 2)
                calc_dt = to_date

                monitoring_rep.append((mrid, machine_id, param_id,
                                       from_date.strftime('%Y-%m-%d %H:%M:%S'),
                                       to_date.strftime('%Y-%m-%d %H:%M:%S'),
                                       state_time, shift,
                                       calc_dt.strftime('%Y-%m-%d %H:%M:%S'),
                                       random.randint(1, 10)))
                mrid += 1

    cursor.executemany("INSERT INTO rep_monitoring_by_priority VALUES (?,?,?,?,?,?,?,?,?)", monitoring_rep)

    # ========== REP: Сводная аналитика по цехам (6 месяцев) ==========
    main_analytics = []
    maid = 1
    for month_offset in range(6):
        month_start = datetime(now.year, now.month, 1) - timedelta(days=30 * month_offset)
        for dept_num in [5, 12, 32]:
            people = random.randint(12, 18)
            hr_fund = round(people * 168, 2)  # часов в месяц
            hr_lose = round(random.uniform(50, 300), 2)
            machine_load = round(random.uniform(500, 1200), 2)
            machine_break = round(random.uniform(50, 200), 2)
            machine_fund = round(machine_load + machine_break + random.uniform(100, 300), 2)

            main_analytics.append((maid, dept_num,
                                   month_start.strftime('%Y-%m-%d'),
                                   hr_fund, hr_lose, people,
                                   machine_load, machine_break, machine_fund,
                                   round(machine_fund * 1.2, 2),
                                   round(random.uniform(1, 15), 2),
                                   round(random.uniform(1, 5), 2),
                                   people, people))
            maid += 1

    cursor.executemany("INSERT INTO rep_main_analitic VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", main_analytics)

    # ========== REP: Дневная аналитика сотрудников (20 дней × 40 чел) ==========
    daily_analytics = []
    daid = 1
    for day_offset in range(20):
        day = now - timedelta(days=day_offset)
        if day.weekday() >= 5:
            continue
        for wid in range(1, 41):
            dept_num = random.choice([5, 12, 32])
            work_time = round(random.uniform(6.0, 10.0), 2)
            parts_count = random.randint(5, 80)
            plan_time = round(parts_count * random.uniform(0.3, 0.8), 2)
            fact_time = round(parts_count * random.uniform(0.25, 0.75), 2)
            downtime = round(random.uniform(0, 2.0), 2)
            fond = round(work_time + random.uniform(0, 1.0), 2)

            daily_analytics.append((daid, day.strftime('%Y-%m-%d'), wid,
                                    random.randint(1, 8), dept_num,
                                    work_time, parts_count, plan_time, fact_time,
                                    downtime, fond, 'active'))
            daid += 1

    cursor.executemany("INSERT INTO rep_daily_worker_analytic VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", daily_analytics)

    conn.commit()


def main():
    print("Создание базы данных...")
    conn = create_connection()
    print("Создание таблиц...")
    create_tables(conn)
    print("Заполнение данными...")
    fill_data(conn)

    # Проверка
    cursor = conn.cursor()
    tables = ['mdc_machine', 'mdc_dept', 'mdc_machine_param', 'mdc_group_param',
              'mdc_machine_param_in_group', 'mdc_param_in_machine', 'mdc_monitoring_value_129',
              'mdc_operating_program_execution_log', 'mdc_operating_program_assembly_unit',
              'mdc_shedule_base', 'mdc_shedule_base_item', 'mdc_shedule_meta',
              'mdc_technology_control_setting', 'mdc_technology_control_log', 'mdc_technology_control_type',
              'hr_dept', 'hr_worker', 'hr_work_position', 'hr_time_sheet', 'hr_time_sheet_type',
              'hr_transfers_personnel', 'hr_worker_fired_dept',
              'rep_monitoring_by_priority', 'rep_main_analitic', 'rep_daily_worker_analytic',
              'tp_assembly_unit', 'tp_technology_operation']

    print("\nСтатистика заполненности:")
    print("-" * 60)
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table:45s} {count:>6d} записей")
    print("-" * 60)

    conn.close()
    print(f"\n✅ База данных создана: {DB_PATH}")


if __name__ == '__main__':
    main()
