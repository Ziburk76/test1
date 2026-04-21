# Актуальная схема базы данных (database.db)
_Сгенерировано автоматически_

## Таблица: mdc_dept
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| name | VARCHAR(255) | NO | NULL | NO |
| parent_id | INTEGER | NO | NULL | NO |
| integration_id | VARCHAR(255) | NO | NULL | NO |

### Примеры данных:
| id | name | parent_id | integration_id |
| --- | --- | --- | --- |
| 1 | Цех №5 — Механообрабатывающий | None | MDC_DEPT_5 |
| 2 | Цех №12 — Сборочный | None | MDC_DEPT_12 |
| 3 | Цех №32 — Термический | None | MDC_DEPT_32 |

## Таблица: mdc_group_param
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| name | VARCHAR(200) | NO | NULL | NO |
| parent_id | INTEGER | NO | NULL | NO |
| short_name | VARCHAR(255) | NO | NULL | NO |
| color | INTEGER | NO | NULL | NO |
| plan_value | NUMERIC(18,2) | NO | NULL | NO |

### Примеры данных:
| id | name | parent_id | short_name | color | plan_value |
| --- | --- | --- | --- | --- | --- |
| 1 | Производство | None | Пр-во | 43520 | 85 |
| 2 | Простой | None | Простой | 16711680 | 5 |
| 3 | Наладка | None | Наладка | 16755200 | 8 |

## Таблица: mdc_machine
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| name | VARCHAR(255) | NO | NULL | NO |
| short_name | VARCHAR(50) | NO | NULL | NO |
| num | VARCHAR(50) | NO | NULL | NO |
| dept_id | INTEGER | NO | NULL | NO |
| _root_num | INTEGER | NO | NULL | NO |
| _root_num_x | INTEGER | NO | NULL | NO |
| integration_id | VARCHAR(255) | NO | NULL | NO |
| dt_commissioning | TIMESTAMP | NO | NULL | NO |
| dt_decommissioning | TIMESTAMP | NO | NULL | NO |
| oeeplan | NUMERIC(18,2) | NO | NULL | NO |

### Примеры данных:
| id | name | short_name | num | dept_id | _root_num | _root_num_x | integration_id | dt_commissioning | dt_decommissioning | oeeplan |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | ЗУБ-9074 Лазерный станок, модели SAMSUNG LCV-2586 | ЗУБ-9074 | ЗУБ-9074 | 1 | 5 | 5 | INT_ZUB_9074 | 2020-03-15 00:00:00 | None | 82.5 |
| 2 | ШЛФ-1414 Токарный станок, модели DMG MORI NLX-3499 | ШЛФ-1414 | ШЛФ-1414 | 1 | 5 | 5 | INT_SHLF_1414 | 2019-07-20 00:00:00 | None | 78 |
| 3 | СВР-8274 Токарно-карусельный станок, модели DMG MORI NLX-9075 | СВР-8274 | СВР-8274 | 1 | 5 | 5 | INT_SVR_8274 | 2021-01-10 00:00:00 | None | 75 |

## Таблица: mdc_machine_param
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| name | VARCHAR(255) | NO | NULL | NO |
| short_name | VARCHAR(255) | NO | NULL | NO |
| parent_id | INTEGER | NO | NULL | NO |
| priority | INTEGER | NO | NULL | NO |
| code | INTEGER | NO | NULL | NO |
| is_service_state | INTEGER | NO | NULL | NO |
| is_by_shedule | INTEGER | NO | NULL | NO |

### Примеры данных:
| id | name | short_name | parent_id | priority | code | is_service_state | is_by_shedule |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Работа | Работа | None | 1 | 1 | 0 | 1 |
| 2 | Простой — нет задания | Нет задания | None | 2 | 10 | 0 | 0 |
| 3 | Простой — ожидание инструмента | Ож. инструмент | None | 3 | 11 | 0 | 0 |

## Таблица: mdc_machine_param_in_group
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| mdc_machine_param_id | INTEGER | NO | NULL | NO |
| mdc_group_param_id | INTEGER | NO | NULL | NO |

### Примеры данных:
| id | mdc_machine_param_id | mdc_group_param_id |
| --- | --- | --- |
| 1 | 1 | 1 |
| 2 | 10 | 1 |
| 3 | 2 | 2 |

## Таблица: mdc_param_in_machine
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| machine_id | INTEGER | NO | NULL | NO |
| machine_param_id | INTEGER | NO | NULL | NO |

### Примеры данных:
| id | machine_id | machine_param_id |
| --- | --- | --- |
| 1 | 1 | 1 |
| 2 | 1 | 2 |
| 3 | 1 | 3 |

## Таблица: mdc_monitoring_value_129
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| machine_id | INTEGER | NO | NULL | NO |
| start_time | TIMESTAMP | NO | NULL | NO |
| end_time | TIMESTAMP | NO | NULL | NO |
| param_in_machine_id | INTEGER | NO | NULL | NO |
| machine_param_id | INTEGER | NO | NULL | NO |

### Примеры данных:
| id | machine_id | start_time | end_time | param_in_machine_id | machine_param_id |
| --- | --- | --- | --- | --- | --- |
| 1 | 1 | 2026-01-05 15:07:56 | 2026-01-05 16:13:56 | 1 | 1 |
| 2 | 1 | 2026-01-05 16:13:56 | 2026-01-05 16:35:56 | 2 | 6 |
| 3 | 1 | 2026-01-05 16:35:56 | 2026-01-05 17:31:56 | 3 | 10 |

## Таблица: mdc_operating_program_execution_log
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| machine_id | INTEGER | NO | NULL | NO |
| worker_id | INTEGER | NO | NULL | NO |
| name_up | VARCHAR(255) | NO | NULL | NO |
| dt_start | TIMESTAMP | NO | NULL | NO |
| dt_end | TIMESTAMP | NO | NULL | NO |
| processing_time | NUMERIC(18,2) | NO | NULL | NO |

### Примеры данных:
| id | machine_id | worker_id | name_up | dt_start | dt_end | processing_time |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | 19 | PROG_DISK_DT55_OP50.NC | 2026-03-09 02:08:56 | 2026-03-09 03:56:20 | 1.79 |
| 2 | 1 | 20 | PROG_OS_AO22_OP10.NC | 2026-03-22 11:38:56 | 2026-03-22 12:58:08 | 1.32 |
| 3 | 1 | 10 | PROG_KORPUS_R250_OP10.NC | 2026-03-30 14:30:56 | 2026-03-30 19:49:32 | 5.31 |

## Таблица: mdc_operating_program_assembly_unit
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| machine_id | INTEGER | NO | NULL | NO |
| name_up | VARCHAR(255) | NO | NULL | NO |
| id_assembly_unit | INTEGER | NO | NULL | NO |

### Примеры данных:
| id | machine_id | name_up | id_assembly_unit |
| --- | --- | --- | --- |
| 1 | 1 | PROG_DISK_DT55_OP50.NC | 6 |
| 2 | 1 | PROG_OS_AO22_OP10.NC | 1 |
| 3 | 1 | PROG_KORPUS_R250_OP10.NC | 6 |

## Таблица: mdc_shedule_base
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| name | VARCHAR(255) | NO | NULL | NO |
| week_day_num | INTEGER | NO | NULL | NO |
| smena_num | INTEGER | NO | NULL | NO |
| dept_id | INTEGER | NO | NULL | NO |
| machine_id | INTEGER | NO | NULL | NO |
| shedule_meta_id | INTEGER | NO | NULL | NO |

### Примеры данных:
| id | name | week_day_num | smena_num | dept_id | machine_id | shedule_meta_id |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Расписание станка 1 — ПН | 1 | 1 | 1 | 1 | None |
| 2 | Расписание станка 1 — ПН | 2 | 1 | 1 | 1 | None |
| 3 | Расписание станка 1 — ПН | 3 | 1 | 1 | 1 | None |

## Таблица: mdc_shedule_base_item
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| shedule_base_id | INTEGER | NO | NULL | NO |
| time_from | TIME | NO | NULL | NO |
| time_to | TIME | NO | NULL | NO |

### Примеры данных:
| id | shedule_base_id | time_from | time_to |
| --- | --- | --- | --- |
| 1 | 1 | 08:00:00 | 12:00:00 |
| 2 | 1 | 13:00:00 | 17:00:00 |
| 3 | 2 | 08:00:00 | 12:00:00 |

## Таблица: mdc_shedule_meta
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| is_holiday | INTEGER | NO | NULL | NO |
| shedule_date | TIMESTAMP | NO | NULL | NO |
| dept_id | INTEGER | NO | NULL | NO |
| machine_id | INTEGER | NO | NULL | NO |
| shedule_type_id | INTEGER | NO | NULL | NO |

### Примеры данных:
| id | is_holiday | shedule_date | dept_id | machine_id | shedule_type_id |
| --- | --- | --- | --- | --- | --- |
| 1 | 1 | 2025-01-01 | None | None | 1 |
| 2 | 1 | 2025-01-07 | None | None | 1 |
| 3 | 1 | 2025-02-23 | None | None | 1 |

## Таблица: mdc_technology_control_setting
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| name | VARCHAR(255) | NO | NULL | NO |
| group_param_id | INTEGER | NO | NULL | NO |
| machine_param_id | INTEGER | NO | NULL | NO |

### Примеры данных:
| id | name | group_param_id | machine_param_id |
| --- | --- | --- | --- |
| 1 | Контроль температуры шпинделя | 1 | 1 |
| 2 | Контроль вибрации | 2 | 1 |
| 3 | Контроль температуры печи | 1 | 9 |

## Таблица: mdc_technology_control_log
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| technology_control_setting_id | INTEGER | NO | NULL | NO |
| param_in_machine_id | INTEGER | NO | NULL | NO |
| param_value | NUMERIC(18,2) | NO | NULL | NO |
| dt_start | TIMESTAMP | NO | NULL | NO |
| dt_end | TIMESTAMP | NO | NULL | NO |
| technology_operation_id | INTEGER | NO | NULL | NO |

### Примеры данных:
| id | technology_control_setting_id | param_in_machine_id | param_value | dt_start | dt_end | technology_operation_id |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | 76 | 37.65 | 2026-01-30 22:07:56 | 2026-01-30 22:47:56 | 6 |
| 2 | 1 | 80 | 125.41 | 2026-01-13 05:07:56 | 2026-01-13 05:27:56 | 5 |
| 3 | 5 | 55 | 58.15 | 2026-03-22 14:07:56 | 2026-03-22 14:31:56 | 3 |

## Таблица: mdc_technology_control_type
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| technology_control_setting_id | INTEGER | NO | NULL | NO |
| type_id | INTEGER | NO | NULL | NO |
| is_tolerance | INTEGER | NO | NULL | NO |
| is_emergency | INTEGER | NO | NULL | NO |

### Примеры данных:
| id | technology_control_setting_id | type_id | is_tolerance | is_emergency |
| --- | --- | --- | --- | --- |
| 1 | 1 | 1 | 1 | 0 |
| 2 | 1 | 2 | 0 | 0 |
| 3 | 2 | 1 | 0 | 1 |

## Таблица: hr_dept
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| name | VARCHAR(255) | NO | NULL | NO |
| parent_id | INTEGER | NO | NULL | NO |
| root_num | INTEGER | NO | NULL | NO |
| integration_id | VARCHAR(255) | NO | NULL | NO |

### Примеры данных:
| id | name | parent_id | root_num | integration_id |
| --- | --- | --- | --- | --- |
| 1 | Цех №5 — Механообрабатывающий | None | 5 | HR_DEPT_5 |
| 2 | Цех №12 — Сборочный | None | 12 | HR_DEPT_12 |
| 3 | Цех №32 — Термический | None | 32 | HR_DEPT_32 |

## Таблица: hr_work_position
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| name | VARCHAR(255) | NO | NULL | NO |

### Примеры данных:
| id | name |
| --- | --- |
| 1 | Оператор станков с ЧПУ |
| 2 | Наладчик станков |
| 3 | Слесарь-сборщик |

## Таблица: hr_worker
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| surname | VARCHAR(50) | NO | NULL | NO |
| name | VARCHAR(50) | NO | NULL | NO |
| patronymic | VARCHAR(50) | NO | NULL | NO |
| personal_num | VARCHAR(50) | NO | NULL | NO |
| smart_card_code | INTEGER | NO | NULL | NO |
| hr_dept_id | INTEGER | NO | NULL | NO |
| dept_num | INTEGER | NO | NULL | NO |
| prof_name | VARCHAR(255) | NO | NULL | NO |
| dt_accept | TIMESTAMP | NO | NULL | NO |
| dt_fired | TIMESTAMP | NO | NULL | NO |
| is_deleted | INTEGER | NO | NULL | NO |

### Примеры данных:
| id | surname | name | patronymic | personal_num | smart_card_code | hr_dept_id | dept_num | prof_name | dt_accept | dt_fired | is_deleted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Сидоров | Артём | Александрович | TN-0001 | 100001 | 6 | 12 | Инженер-технолог | 2020-04-19 00:00:00 | None | 0 |
| 2 | Кузнецов | Михаил | Иванович | TN-0002 | 100002 | 3 | 32 | Термист | 2020-04-23 00:00:00 | None | 0 |
| 3 | Семёнов | Михаил | Андреевич | TN-0003 | 100003 | 1 | 5 | Наладчик станков | 2020-07-09 00:00:00 | None | 0 |

## Таблица: hr_time_sheet_type
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| name | VARCHAR(255) | NO | NULL | NO |

### Примеры данных:
| id | name |
| --- | --- |
| 1 | Рабочее время |
| 2 | Ночные часы |
| 3 | Сверхурочные |

## Таблица: hr_time_sheet
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| dt_day | TIMESTAMP | NO | NULL | NO |
| hr_worker_id | INTEGER | NO | NULL | NO |
| hr_time_sheet_type_id | INTEGER | NO | NULL | NO |
| time | NUMERIC(5,2) | NO | NULL | NO |

### Примеры данных:
| id | dt_day | hr_worker_id | hr_time_sheet_type_id | time |
| --- | --- | --- | --- | --- |
| 1 | 2026-04-03 | 1 | 1 | 8.09 |
| 2 | 2026-04-03 | 2 | 1 | 7.47 |
| 3 | 2026-04-03 | 3 | 1 | 8.32 |

## Таблица: hr_transfers_personnel
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| unique_code | INTEGER | NO | NULL | NO |
| hr_dept_id | INTEGER | NO | NULL | NO |
| dept_num | INTEGER | NO | NULL | NO |
| tab_num | INTEGER | NO | NULL | NO |
| dt_accept | TIMESTAMP | NO | NULL | NO |
| dt_fired | TIMESTAMP | NO | NULL | NO |
| is_type | INTEGER | NO | NULL | NO |

### Примеры данных:
| id | unique_code | hr_dept_id | dept_num | tab_num | dt_accept | dt_fired | is_type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 100001 | 6 | 12 | 1 | 2020-04-19 00:00:00 | None | 0 |
| 2 | 100002 | 3 | 32 | 2 | 2020-04-23 00:00:00 | None | 0 |
| 3 | 100003 | 1 | 5 | 3 | 2020-07-09 00:00:00 | None | 0 |

## Таблица: hr_worker_fired_dept
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| dt_day | TIMESTAMP | NO | NULL | NO |
| dept_num | INTEGER | NO | NULL | NO |
| begin_month_num | INTEGER | NO | NULL | NO |
| worker_fired_num | INTEGER | NO | NULL | NO |
| average_headcount_perscent | REAL | NO | NULL | NO |

### Примеры данных:
| id | dt_day | dept_num | begin_month_num | worker_fired_num | average_headcount_perscent |
| --- | --- | --- | --- | --- | --- |
| 1 | 2026-04-01 | 5 | 12 | 1 | 8.33 |
| 2 | 2026-04-01 | 12 | 16 | 1 | 6.25 |
| 3 | 2026-04-01 | 32 | 16 | 2 | 12.5 |

## Таблица: rep_monitoring_by_priority
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| mdc_machineid | INTEGER | NO | NULL | NO |
| mdc_machine_param_id | INTEGER | NO | NULL | NO |
| from_date | TIMESTAMP | NO | NULL | NO |
| to_date | TIMESTAMP | NO | NULL | NO |
| state_time | INTEGER | NO | NULL | NO |
| shift_num | INTEGER | NO | NULL | NO |
| dt_calc | TIMESTAMP | NO | NULL | NO |
| tp_technology_operation_id | INTEGER | NO | NULL | NO |

### Примеры данных:
| id | mdc_machineid | mdc_machine_param_id | from_date | to_date | state_time | shift_num | dt_calc | tp_technology_operation_id |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | 1 | 2026-03-06 15:07:56 | 2026-04-05 15:07:56 | 79403 | 2 | 2026-04-05 15:07:56 | 5 |
| 2 | 1 | 2 | 2026-03-06 15:07:56 | 2026-04-05 15:07:56 | 36240 | 1 | 2026-04-05 15:07:56 | 7 |
| 3 | 1 | 4 | 2026-03-06 15:07:56 | 2026-04-05 15:07:56 | 37023 | 2 | 2026-04-05 15:07:56 | 1 |

## Таблица: rep_main_analitic
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| dept_num | INTEGER | NO | NULL | NO |
| dt_of_month | TIMESTAMP | NO | NULL | NO |
| hr_fund_time | NUMERIC(18,4) | NO | NULL | NO |
| hr_lose_time | NUMERIC(18,4) | NO | NULL | NO |
| hr_people_count | NUMERIC(18,4) | NO | NULL | NO |
| mdc_machine_load_time | NUMERIC(18,4) | NO | NULL | NO |
| mdc_machine_break_time | NUMERIC(18,4) | NO | NULL | NO |
| mdc_machine_fund | NUMERIC(18,4) | NO | NULL | NO |
| mdc_machine_fund_24 | NUMERIC(18,4) | NO | NULL | NO |
| qa_defective_part_count | NUMERIC(18,4) | NO | NULL | NO |
| staff_turnover | NUMERIC(12,5) | NO | NULL | NO |
| hr_worker_count | INTEGER | NO | NULL | NO |
| hr_people_count_plan | INTEGER | NO | NULL | NO |

### Примеры данных:
| id | dept_num | dt_of_month | hr_fund_time | hr_lose_time | hr_people_count | mdc_machine_load_time | mdc_machine_break_time | mdc_machine_fund | mdc_machine_fund_24 | qa_defective_part_count | staff_turnover | hr_worker_count | hr_people_count_plan |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 5 | 2026-04-01 | 2352 | 231.37 | 14 | 593.98 | 141.51 | 974.93 | 1169.92 | 10.43 | 2.36 | 14 | 14 |
| 2 | 12 | 2026-04-01 | 2352 | 221.71 | 14 | 540.27 | 177.94 | 865.97 | 1039.16 | 13.83 | 1.84 | 14 | 14 |
| 3 | 32 | 2026-04-01 | 3024 | 255.98 | 18 | 636.03 | 128.93 | 982.38 | 1178.86 | 13.37 | 1.49 | 18 | 18 |

## Таблица: rep_daily_worker_analytic
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| dt_day | DATE | NO | NULL | NO |
| hr_worker_id | INTEGER | NO | NULL | NO |
| hr_work_position_id | INTEGER | NO | NULL | NO |
| dept_num | INTEGER | NO | NULL | NO |
| work_time | NUMERIC | NO | NULL | NO |
| manufactured_parts_log_count | BIGINT | NO | NULL | NO |
| manufactured_parts_log_plan_time | NUMERIC | NO | NULL | NO |
| manufactured_parts_log_fact_time | NUMERIC | NO | NULL | NO |
| downtime | NUMERIC | NO | NULL | NO |
| fond | NUMERIC | NO | NULL | NO |
| status | VARCHAR(255) | NO | NULL | NO |

### Примеры данных:
| id | dt_day | hr_worker_id | hr_work_position_id | dept_num | work_time | manufactured_parts_log_count | manufactured_parts_log_plan_time | manufactured_parts_log_fact_time | downtime | fond | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2026-04-03 | 1 | 1 | 12 | 7.74 | 10 | 5.6 | 2.98 | 1.49 | 8.17 | active |
| 2 | 2026-04-03 | 2 | 2 | 5 | 9.78 | 12 | 6.72 | 4.22 | 0.78 | 10.66 | active |
| 3 | 2026-04-03 | 3 | 4 | 5 | 7.55 | 63 | 21.19 | 45.37 | 0.43 | 8.5 | active |

## Таблица: tp_assembly_unit
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| name | VARCHAR(255) | NO | NULL | NO |

### Примеры данных:
| id | name |
| --- | --- |
| 1 | Корпус редуктора Р-250 |
| 2 | Вал приводной ВП-12 |
| 3 | Шестерня коническая ШК-45 |

## Таблица: tp_technology_operation
| Column | Type | Not Null | Default | PK |
|--------|------|----------|---------|----|
| id | INTEGER | NO | NULL | YES |
| code | VARCHAR(30) | NO | NULL | NO |
| description | TEXT | NO | NULL | NO |
| machine_time | INTEGER | NO | NULL | NO |
| piece_time | NUMERIC(18,5) | NO | NULL | NO |

### Примеры данных:
| id | code | description | machine_time | piece_time |
| --- | --- | --- | --- | --- |
| 1 | TO-001 | Токарная черновая обработка корпуса | 120 | 45.5 |
| 2 | TO-002 | Токарная чистовая обработка корпуса | 90 | 35.2 |
| 3 | TO-003 | Фрезерная обработка плоскостей | 75 | 28.8 |
