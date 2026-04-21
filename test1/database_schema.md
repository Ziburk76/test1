## Описание базы данных для чат-бота по оборудованию и персоналу

Данный документ содержит структуру и логические связи таблиц, необходимых для ответов на вопросы о работе оборудования (станков) и связанных с ними данных по персоналу. База данных SQLite, связи между таблицами реализованы через идентификаторы (поля с суффиксом `_id`), но внешние ключи могут отсутствовать – при составлении запросов следует использовать логические соединения по совпадению значений.

---

### 1. Таблицы, относящиеся к оборудованию (MDC)

#### 1.1. `mdc_machine` – станки
| Поле | Тип | Описание | Связи |
|------|-----|----------|-------|
| `id` | int | Уникальный идентификатор станка | PK |
| `name` | varchar | Полное наименование станка | |
| `short_name` | varchar | Краткое наименование | |
| `num` | varchar | Инвентарный номер | |
| `dept_id` | int | Подразделение (цех) | → `mdc_dept.id` |
| `_root_num` | int | Номер цеха в объектной модели | → `hr_dept.root_num` (логически) |
| `_root_num_x` | int | То же, альтернативное поле | → `hr_dept.root_num` |
| `integration_id` | varchar | Внешний идентификатор из СМПО | |
| `dt_commissioning` | timestamp | Дата ввода в эксплуатацию | |
| `dt_decommissioning` | timestamp | Дата вывода | |
| `oeeplan` | numeric | Плановый OEE | |

#### 1.2. `mdc_dept` – подразделения (цеха) из системы MDC
| Поле | Тип | Описание | Связи |
|------|-----|----------|-------|
| `id` | int | PK | |
| `name` | varchar | Название подразделения | |
| `parent_id` | int | Родительское подразделение | → `mdc_dept.id` |
| `integration_id` | varchar | Внешний идентификатор | |

#### 1.3. `mdc_machine_param` – состояния и причины простоев
| Поле | Тип | Описание | Связи |
|------|-----|----------|-------|
| `id` | int | PK | |
| `name` | varchar | Наименование состояния (например, «Простой станка») | |
| `short_name` | varchar | Краткое имя | |
| `parent_id` | int | Родительское состояние (иерархия) | → `mdc_machine_param.id` |
| `priority` | int | Приоритет (чем меньше, тем выше) | |
| `code` | int | Код состояния | |
| `is_service_state` | int | 1 – сервисное состояние | |
| `is_by_shedule` | int | Учитывается в расписании | |

#### 1.4. `mdc_group_param` – группы состояний
| Поле | Тип | Описание | Связи |
|------|-----|----------|-------|
| `id` | int | PK | |
| `name` | varchar | Название группы (например, «Производство», «Простой») | |
| `parent_id` | int | Родительская группа | → `mdc_group_param.id` |
| `short_name` | varchar | Краткое имя | |
| `color` | int | Цвет для отображения | |
| `plan_value` | numeric | Плановое значение (процент) | |

#### 1.5. `mdc_machine_param_in_group` – связь состояний и групп (many-to-many)
| Поле | Тип | Описание | Связи |
|------|-----|----------|-------|
| `id` | int | PK | |
| `mdc_machine_param_id` | int | Состояние | → `mdc_machine_param.id` |
| `mdc_group_param_id` | int | Группа | → `mdc_group_param.id` |

#### 1.6. `mdc_param_in_machine` – какие состояния отслеживаются на конкретном станке
| Поле | Тип | Описание | Связи |
|------|-----|----------|-------|
| `id` | int | PK | |
| `machine_id` | int | Станок | → `mdc_machine.id` |
| `machine_param_id` | int | Состояние | → `mdc_machine_param.id` |

#### 1.7. `mdc_monitoring_value_129` – история срабатываний состояний (для параметра 129)
| Поле | Тип | Описание | Связи |
|------|-----|----------|-------|
| `id` | int | PK | |
| `machine_id` | int | Станок | → `mdc_machine.id` |
| `start_time` | timestamp | Начало интервала | |
| `end_time` | timestamp | Конец интервала | |
| `param_in_machine_id` | int | Связь с параметром на станке | → `mdc_param_in_machine.id` |
| `machine_param_id` | int | Состояние | → `mdc_machine_param.id` |

#### 1.8. `mdc_operating_program_execution_log` – лог выполнения программ на станке
| Поле | Тип | Описание | Связи |
|------|-----|----------|-------|
| `id` | int | PK | |
| `machine_id` | int | Станок | → `mdc_machine.id` |
| `worker_id` | int | Сотрудник, работавший на станке | → `hr_worker.id` |
| `name_up` | varchar | Имя управляющей программы | |
| `dt_start` | timestamp | Начало выполнения | |
| `dt_end` | timestamp | Окончание | |
| `processing_time` | numeric | Время обработки (в часах?) | |

#### 1.9. `mdc_operating_program_assembly_unit` – привязка программ к сборочным единицам (деталям)
| Поле | Тип | Описание | Связи |
|------|-----|----------|-------|
| `id` | int | PK | |
| `machine_id` | int | Станок | → `mdc_machine.id` |
| `name_up` | varchar | Имя программы | |
| `id_assembly_unit` | int | Сборочная единица | → `tp_assembly_unit.id` |

#### 1.10. `mdc_shedule_base` – базовое расписание (режимы работы)
| Поле | Тип | Описание | Связи |
|------|-----|----------|-------|
| `id` | int | PK | |
| `name` | varchar | Название расписания (например, «1 смена») | |
| `week_day_num` | int | День недели (1-7) | |
| `smena_num` | int | Номер смены | |
| `dept_id` | int | Цех | → `mdc_dept.id` |
| `machine_id` | int | Станок | → `mdc_machine.id` |
| `shedule_meta_id` | int | Метаданные расписания | → `mdc_shedule_meta.id` |

#### 1.11. `mdc_shedule_base_item` – временные интервалы расписания
| Поле | Тип | Описание | Связи |
|------|-----|----------|-------|
| `id` | int | PK | |
| `shedule_base_id` | int | Расписание | → `mdc_shedule_base.id` |
| `time_from` | time | Время начала | |
| `time_to` | time | Время окончания | |

#### 1.12. `mdc_shedule_meta` – особые даты (праздники)
| Поле | Тип | Описание | Связи |
|------|-----|----------|-------|
| `id` | int | PK | |
| `is_holiday` | int | 1 – выходной/праздник | |
| `shedule_date` | timestamp | Дата | |
| `dept_id` | int | Цех | → `mdc_dept.id` |
| `machine_id` | int | Станок | → `mdc_machine.id` |
| `shedule_type_id` | int | Тип расписания | |

#### 1.13. `mdc_technology_control_setting` – настройки контроля параметров
| Поле | Тип | Описание | Связи |
|------|-----|----------|-------|
| `id` | int | PK | |
| `name` | varchar | Название настройки | |
| `group_param_id` | int | Группа состояний | → `mdc_group_param.id` |
| `machine_param_id` | int | Контролируемый параметр | → `mdc_machine_param.id` |

#### 1.14. `mdc_technology_control_log` – журнал нарушений контроля
| Поле | Тип | Описание | Связи |
|------|-----|----------|-------|
| `id` | int | PK | |
| `technology_control_setting_id` | int | Настройка | → `mdc_technology_control_setting.id` |
| `param_in_machine_id` | int | Параметр на станке | → `mdc_param_in_machine.id` |
| `param_value` | numeric | Зафиксированное значение | |
| `dt_start` | timestamp | Начало нарушения | |
| `dt_end` | timestamp | Конец нарушения | |
| `technology_operation_id` | int | Технологическая операция | → `tp_technology_operation.id` |

---

### 2. Таблицы, относящиеся к персоналу (HR)

#### 2.1. `hr_worker` – сотрудники
| Поле | Тип | Описание | Связи |
|------|-----|----------|-------|
| `id` | int | PK | |
| `surname` | varchar | Фамилия | |
| `name` | varchar | Имя | |
| `patronymic` | varchar | Отчество | |
| `personal_num` | varchar | Табельный номер | |
| `smart_card_code` | int | Уникальный код сотрудника | |
| `hr_dept_id` | int | Подразделение (цех) | → `hr_dept.id` |
| `dept_num` | int | Номер цеха (дублирует) | → `hr_dept.root_num` |
| `prof_name` | varchar | Наименование профессии | |
| `dt_accept` | timestamp | Дата приёма | |
| `dt_fired` | timestamp | Дата увольнения | |
| `is_deleted` | int | 1 – уволен | |

#### 2.2. `hr_dept` – подразделения из 1С ЗУП
| Поле | Тип | Описание | Связи |
|------|-----|----------|-------|
| `id` | int | PK | |
| `name` | varchar | Название цеха/участка | |
| `parent_id` | int | Родительское подразделение | → `hr_dept.id` |
| `root_num` | int | Номер корневого цеха (например, 5, 32) | → `mdc_machine._root_num_x` |
| `integration_id` | varchar | Внешний идентификатор | |

#### 2.3. `hr_work_position` – должности
| Поле | Тип | Описание | Связи |
|------|-----|----------|-------|
| `id` | int | PK | |
| `name` | varchar | Наименование должности | |

#### 2.4. `hr_time_sheet` – учёт рабочего времени
| Поле | Тип | Описание | Связи |
|------|-----|----------|-------|
| `id` | int | PK | |
| `dt_day` | timestamp | Дата | |
| `hr_worker_id` | int | Сотрудник | → `hr_worker.id` |
| `hr_time_sheet_type_id` | int | Тип трудозатрат | → `hr_time_sheet_type.id` |
| `time` | numeric | Количество часов | |

#### 2.5. `hr_time_sheet_type` – виды трудозатрат
| Поле | Тип | Описание |
|------|-----|----------|
| `id` | int | PK |
| `name` | varchar | Например, «Ночные часы» |

#### 2.6. `hr_transfers_personnel` – кадровые перемещения
| Поле | Тип | Описание | Связи |
|------|-----|----------|-------|
| `id` | int | PK | |
| `unique_code` | int | Код сотрудника (похож на `smart_card_code`) | |
| `hr_dept_id` | int | Подразделение | → `hr_dept.id` |
| `dept_num` | int | Номер цеха | |
| `tab_num` | int | Табельный номер | |
| `dt_accept` | timestamp | Дата приёма/перевода | |
| `dt_fired` | timestamp | Дата увольнения | |
| `is_type` | int | 0 – приём, 1 – увольнение | |

#### 2.7. `hr_worker_fired_dept` – статистика увольнений по цехам
| Поле | Тип | Описание | Связи |
|------|-----|----------|-------|
| `id` | int | PK | |
| `dt_day` | timestamp | Дата (начало месяца) | |
| `dept_num` | int | Номер цеха | |
| `begin_month_num` | int | Число работников на начало месяца | |
| `worker_fired_num` | int | Число уволившихся за месяц | |

---

### 3. Аналитические таблицы (REP)

#### 3.1. `rep_monitoring_by_priority` – агрегированные данные по состояниям станков
| Поле | Тип | Описание | Связи |
|------|-----|----------|-------|
| `id` | int | PK | |
| `mdc_machineid` | int | Станок | → `mdc_machine.id` |
| `mdc_machine_param_id` | int | Состояние | → `mdc_machine_param.id` |
| `from_date` | timestamp | Начало периода | |
| `to_date` | timestamp | Конец периода | |
| `state_time` | int | Длительность состояния (секунды) | |
| `shift_num` | int | Номер смены | |
| `dt_calc` | timestamp | Дата расчёта | |
| `tp_technology_operation_id` | int | Технологическая операция | → `tp_technology_operation.id` |
| `rep_machine_oee_id` | int | Связь с таблицей OEE | → `rep_machine_oee.id` |

#### 3.2. `rep_main_analitic` – сводная аналитика по цехам за месяц
| Поле | Тип | Описание | Связи |
|------|-----|----------|-------|
| `id` | int | PK | |
| `dept_num` | int | Номер цеха | → `hr_dept.root_num` |
| `dt_of_month` | timestamp | Начало месяца | |
| `hr_fund_time` | numeric | Фонд рабочего времени персонала | |
| `hr_lose_time` | numeric | Потери рабочего времени | |
| `hr_people_count` | numeric | Численность | |
| `mdc_machine_load_time` | numeric | Время загрузки станков | |
| `mdc_machine_break_time` | numeric | Время простоев | |
| `mdc_machine_fund` | numeric | Общий фонд времени станков | |
| ... | | и другие показатели | |

#### 3.3. `rep_daily_worker_analytic` – дневная аналитика по сотрудникам
| Поле | Тип | Описание | Связи |
|------|-----|----------|-------|
| `id` | int | PK | |
| `dt_day` | date | Дата | |
| `hr_worker_id` | int | Сотрудник | → `hr_worker.id` |
| `hr_work_position_id` | int | Должность | → `hr_work_position.id` |
| `dept_num` | int | Цех | |
| `work_time` | numeric | Отработанное время | |
| `manufactured_parts_log_count` | int | Количество изготовленных деталей | |
| ... | | | |

---

### 4. Таблицы технологических процессов (TP)

#### 4.1. `tp_technology_operation` – технологические операции
| Поле | Тип | Описание | Связи |
|------|-----|----------|-------|
| `id` | int | PK | |
| `code` | varchar | Код операции | |
| `description` | text | Описание | |
| `machine_time` | int | Машинное время (норма) | |
| `piece_time` | numeric | Штучное время | |

#### 4.2. `tp_assembly_unit` – сборочные единицы (детали)
| Поле | Тип | Описание |
|------|-----|----------|
| `id` | int | PK |
| `name` | varchar | Наименование детали |

---

### 5. Логические связи между таблицами (ключевые JOINs)

| Связь | Таблица A | Поле A | Таблица B | Поле B | Смысл связи |
|-------|-----------|--------|-----------|--------|-------------|
| Станок → Подразделение MDC | `mdc_machine` | `dept_id` | `mdc_dept` | `id` | Станок привязан к цеху в системе MDC |
| Станок → Подразделение HR | `mdc_machine` | `_root_num_x` | `hr_dept` | `root_num` | Сопоставление цеха MDC с цехом 1С |
| Станок → Состояния (лог) | `mdc_monitoring_value_129` | `machine_id` | `mdc_machine` | `id` | Фиксация состояний станка |
| Состояние → Справочник состояний | `mdc_monitoring_value_129` | `machine_param_id` | `mdc_machine_param` | `id` | Расшифровка кода состояния |
| Станок → Выполнение программ | `mdc_operating_program_execution_log` | `machine_id` | `mdc_machine` | `id` | Программы, выполнявшиеся на станке |
| Сотрудник → Выполнение программ | `mdc_operating_program_execution_log` | `worker_id` | `hr_worker` | `id` | Кто работал на станке |
| Программа → Деталь | `mdc_operating_program_assembly_unit` | `name_up`, `machine_id` | `mdc_operating_program_execution_log` | `name_up`, `machine_id` | Какая деталь обрабатывалась по программе |
| Деталь → Техоперация | `mdc_operating_program_assembly_unit` | `id_assembly_unit` | `tp_assembly_unit` | `id` | Привязка программы к детали |
| Аналитика по приоритетам → Станок | `rep_monitoring_by_priority` | `mdc_machineid` | `mdc_machine` | `id` | Сводка по состояниям |
| Аналитика по приоритетам → Техоперация | `rep_monitoring_by_priority` | `tp_technology_operation_id` | `tp_technology_operation` | `id` | Привязка к техоперации |
| Сводная аналитика → Цех | `rep_main_analitic` | `dept_num` | `hr_dept` | `root_num` | Аналитика по цеху |
| Дневная аналитика → Сотрудник | `rep_daily_worker_analytic` | `hr_worker_id` | `hr_worker` | `id` | Производительность сотрудника |
| Журнал нарушений → Настройка контроля | `mdc_technology_control_log` | `technology_control_setting_id` | `mdc_technology_control_setting` | `id` | Нарушение параметров |
| Журнал нарушений → Техоперация | `mdc_technology_control_log` | `technology_operation_id` | `tp_technology_operation` | `id` | Связь нарушения с операцией |

---

### 6. Mermaid-диаграмма логических связей

```mermaid
graph TD
    A[Станок<br>mdc_machine] -->|имеет подразделение| B[Подразделение MDC<br>mdc_dept]
    A -->|сопоставлен с цехом| C[Подразделение HR<br>hr_dept]
    A -->|фиксирует состояния| D[Журнал состояний<br>mdc_monitoring_value_129]
    A -->|выполняет программы| E[Лог выполнения программ<br>mdc_operating_program_execution_log]
    A -->|контролируется настройками| F[Настройки контроля<br>mdc_technology_control_setting]
    
    D -->|ссылается на| G[Справочник состояний<br>mdc_machine_param]
    G -->|входит в группу| H[Группа состояний<br>mdc_group_param]
    
    E -->|выполняется сотрудником| I[Сотрудник<br>hr_worker]
    I -->|работает в| C
    I -->|имеет должность| J[Должность<br>hr_work_position]
    I -->|учитывается в табеле| K[Табель рабочего времени<br>hr_time_sheet]
    
    E -->|использует программу| L[Программа → деталь<br>mdc_operating_program_assembly_unit]
    L -->|обрабатывает| M[Сборочная единица<br>tp_assembly_unit]
    M -->|требует операций| N[Технологическая операция<br>tp_technology_operation]
    
    D -->|агрегируется в| O[Аналитика по состояниям<br>rep_monitoring_by_priority]
    O -->|привязана к| N
    
    P[Сводная аналитика по цеху<br>rep_main_analitic] -->|агрегирует данные по| C
    P -->|включает показатели станков| A
    
    Q[Дневная аналитика сотрудника<br>rep_daily_worker_analytic] -->|детализирует| I
    Q -->|связана с| J
    
    F -->|порождает| R[Журнал нарушений контроля<br>mdc_technology_control_log]
    R -->|относится к| N