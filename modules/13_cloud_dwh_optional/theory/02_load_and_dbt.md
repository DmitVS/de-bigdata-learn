---
type: theory
module: "13"
topic: 2
labs: ["13.1", "13.2"]
tasks: ["1", "2"]
time: "~70 мин"
tags: [snowflake, copy-into, stage, dbt-snowflake]
---

# 02 · Загрузка в Snowflake и перенос dbt-проекта

> [!info] Урок одной фразой
> Чтобы данные оказались в Snowflake, их сначала кладут на «приёмный склад» (stage). Потом
> команда `COPY INTO` раскладывает их по полкам таблицы. dbt-проект переезжает почти без правок:
> меняются адаптер, профиль и пара функций диалекта. Модели, тесты и документация остаются теми же.

> [!todo] Чек-лист: после урока ты сможешь
> - [ ] описать путь файла в таблицу: stage → `COPY INTO`; объяснить, почему повторная загрузка не задвоит данные;
> - [ ] создать таблицу по схеме Parquet (`INFER_SCHEMA`) и загрузить файлы датасета;
> - [ ] настроить профиль dbt-snowflake через переменные окружения;
> - [ ] найти различия диалектов DuckDB и Snowflake в моделях;
> - [ ] проверить проект без подключения (`dbt parse`) и объяснить, что такая проверка не ловит.

> [!warning] Ловушка
> Не клади реквизиты Snowflake в `profiles.yml`. Держи их в `.env` (`SNOWFLAKE_ACCOUNT`,
> `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`): профиль читает их через `env_var`, в git попадает только
> шаблон. SQL Snowflake в уроке проверен по документации — для запуска нужен аккаунт.

**Нужно для:** лабы [13.1](../labs/13.1_load/README.md), [13.2](../labs/13.2_dbt_snowflake/README.md).
**Карта урока:** [load-and-dbt.canvas](../maps/load-and-dbt.canvas).

---

## Шаг 0. Азбука

| Понятие | В аналогии «приёмный склад» | Подробнее |
|---|---|---|
| Stage | Приёмный склад: файлы лежат, но ещё не на полках | [Snowflake](../../../glossary/snowflake.md) |
| `COPY INTO` | Раскладка поставки по полкам с журналом «что уже разложено» | [Snowflake](../../../glossary/snowflake.md) |
| `INFER_SCHEMA` | Опись поставки: какие колонки и типы в файлах | [Snowflake](../../../glossary/snowflake.md) |
| Адаптер dbt | Переводчик dbt на диалект хранилища | [dbt](../../../glossary/dbt-core.md) |

---

## Шаг 1. Путь файла в таблицу

**Проблема.** В lakehouse dlt (модуль 04) писал Parquet прямо в S3, и Iceberg-таблица просто
ссылалась на файлы. В Snowflake хранение — его собственное: файлы надо **загрузить**.

**Как устроено.** Скрипт `demo/snowflake/01_setup_and_load.sql`:

1. **Склад** `de_wh`: `XSMALL`, `AUTO_SUSPEND = 60`, `INITIALLY_SUSPENDED = TRUE` (урок 01).
2. **Stage** — именованное место для файлов: внутреннее (внутри Snowflake) или внешнее (ваш
   S3/GCS/Azure). Файлы кладут командой `PUT` или через интерфейс Snowsight.
3. **`INFER_SCHEMA`** читает схему Parquet, `CREATE TABLE … USING TEMPLATE` создаёт таблицу по ней.
4. **`COPY INTO таблица FROM @stage`** загружает файлы. `MATCH_BY_COLUMN_NAME` сопоставляет колонки
   по именам, а не по порядку.

`COPY INTO` ведёт **журнал загруженных файлов** таблицы (64 дня): повторный запуск пропускает уже
загруженные файлы. Это идемпотентность «из коробки» — то, что мы в модуле 04 делали руками
(защита от повторной доставки файла).

**Что из этого следует.** Загрузка в облачный DWH — тоже пайплайн: файлы → stage → таблица. Его
оркестрируют так же (модуль 06), а `COPY INTO` можно запускать по расписанию или сервисом Snowpipe
при появлении файла.

---

## Шаг 2. Профиль dbt-snowflake

**Проблема.** dbt-проект написан под DuckDB. Что нужно, чтобы он собирался в Snowflake?

**Как устроено.** Адаптер `dbt-snowflake` 1.12 — в группе зависимостей `cloud` образа workspace.
Профиль `demo/dbt_snowflake/profiles.yml`:

```yaml
snowflake_demo:
  target: dev
  outputs:
    dev:
      type: snowflake                                              # ① адаптер
      account: "{{ env_var('SNOWFLAKE_ACCOUNT', '') or 'not-set' }}"   # ② из окружения
      user: "{{ env_var('SNOWFLAKE_USER', '') or 'not-set' }}"
      password: "{{ env_var('SNOWFLAKE_PASSWORD', '') or 'not-set' }}"
      role: "{{ env_var('SNOWFLAKE_ROLE', '') or 'SYSADMIN' }}"
      warehouse: de_wh                                             # ③ склад, который тратит кредиты
      database: de_course
      schema: analytics
```

| Метка | Что важно |
|---|---|
| ① | один проект может иметь несколько целей: `dev` на DuckDB и `snowflake` — на Snowflake |
| ② | `or 'not-set'` позволяет разбирать проект без реквизитов (шаг 4). Значение по умолчанию `env_var` не годится: в workspace переменная **задана, но пуста**, и dbt пишет `Invalid profile: 'user' is a required property` |
| ③ | склад в профиле — тот, на котором dbt выполняет модели; отдельный склад для dbt проще считать в деньгах |

`account` — идентификатор вида `орг-аккаунт` из адреса Snowsight. Для CI и продакшена вместо
пароля — ключевая пара (`private_key_path`): пароли с MFA для сервисных пользователей не годятся.

---

## Шаг 3. Различия диалектов

**Проблема.** SQL — стандарт, но у каждого хранилища свои функции и правила имён. Модель, которая
работает в DuckDB, может не собраться в Snowflake.

**Как устроено.** Что встречается в наших моделях:

| Что | DuckDB / Trino | Snowflake |
|---|---|---|
| Имена колонок из Parquet | как в файле, без кавычек | регистр сохраняется: `"store_id"` в кавычках; без кавычек — `STORE_ID` |
| Условная сумма | `sum(x) filter (where c)`, `count_if(c)` | `sum(iff(c, x, 0))`, `count_if(c)` |
| Дата из строки | `dt::date` | `to_date(dt)` или `dt::date` |
| `CREATE OR REPLACE` таблицы | в Iceberg через DuckDB — нет (модуль 05) | да |
| Материализации | `table` + публикация в Iceberg post-hook | `table`, `incremental` с `merge`, `dynamic_table` |

Учебные модели `demo/dbt_snowflake/` уже переписаны: staging переименовывает колонки из кавычек в
обычные имена, витрина использует `iff`.

**Что из этого следует.** Перенос проекта — это в основном staging: там сосредоточены имена
источников и приведения типов. Витрины поверх staging чаще всего переносятся без правок.

---

## Шаг 4. Проверка без подключения

**Проблема.** Аккаунта может не быть (trial закончился, CI без секретов). Можно ли проверить
проект хотя бы частично?

**Как устроено.** `dbt parse` разбирает проект — YAML, Jinja, `ref`, `source` — и строит граф,
**не подключаясь** к хранилищу. Он поймает опечатку в `ref`, сломанный YAML, цикл зависимостей.
Ошибки SQL диалекта он не поймает: SQL проверяет только хранилище.

> [!example]- Попробуй сам: разбор проекта под Snowflake без аккаунта
> ```bash
> make shell
> cd modules/13_cloud_dwh_optional/demo/dbt_snowflake
> dbt parse
> dbt ls --resource-type model source
> exit
> ```
> **Увидишь:** `Registered adapter: snowflake=1.12.1`, затем `Performance info: …` без ошибок
> (`Found 2 models, 2 data tests, 1 source`);
> список — `snowflake_demo.marts.mart_city_oos_daily`, `snowflake_demo.staging.stg_sales`,
> `source:snowflake_demo.raw.sales`.
> **Почему:** адаптер загружен, граф проекта построен; реквизиты не нужны — профиль берёт
> значения по умолчанию `not-set`. `dbt debug` или `dbt build` без аккаунта упадут на подключении.

---

## Сборка целиком

```mermaid
sequenceDiagram
    autonumber
    participant F as файлы датасета
    participant S as stage
    participant T as raw.sales
    participant DBT as dbt build (склад de_wh)
    participant M as analytics.mart_city_oos_daily
    F->>S: PUT / загрузка в Snowsight
    S->>T: COPY INTO … MATCH_BY_COLUMN_NAME (журнал файлов)
    DBT->>T: stg_sales (view): имена и типы
    DBT->>M: витрина (table): sum, iff, group by
    DBT-->>DBT: тесты not_null; склад засыпает через 60 с
```

| Шаг | Если сломается | Симптом |
|---|---|---|
| 2 | колонки по порядку, а не по имени | данные в чужих колонках |
| 2 | повторный `COPY INTO` | файлы пропущены — это норма (журнал загрузок) |
| 3 | имена колонок без кавычек | `invalid identifier 'STORE_ID'` |

## Шпаргалка

| Хочу | Как |
|---|---|
| Таблица по схеме Parquet | `CREATE TABLE t USING TEMPLATE (SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*)) FROM TABLE(INFER_SCHEMA(…)))` |
| Загрузить | `COPY INTO t FROM @stage FILE_FORMAT=(…) MATCH_BY_COLUMN_NAME=CASE_INSENSITIVE` |
| Перезагрузить файл заново | `COPY INTO … FORCE = TRUE` (осознанно: будут дубли) |
| Профиль dbt | `type: snowflake`, реквизиты через `env_var` |
| Проверка без аккаунта | `dbt parse`, `dbt ls` |
| Проверка подключения | `dbt debug` |

## Типичные ошибки

| Симптом | Причина | Как проверить | Как чинить |
|---|---|---|---|
| `invalid identifier` | регистр имён колонок из Parquet | `DESCRIBE TABLE` | кавычки в staging или `MATCH_BY_COLUMN_NAME` + верхний регистр |
| `COPY INTO` ничего не загрузил | файлы уже в журнале загрузок | `LOAD_HISTORY` | это норма; `FORCE` только осознанно |
| dbt: `Could not connect` | реквизиты не в окружении | `env | grep SNOWFLAKE` в `make shell` | `.env` + пересоздать workspace |
| Склад не выключается | долгие запросы BI или нет `AUTO_SUSPEND` | Query History | `AUTO_SUSPEND`, отдельный склад |

## Проверь себя

Карточки — в [flashcards.md](../flashcards.md).

> [!question] 1. Почему повторный `COPY INTO` того же файла не создаёт дубли?
> > [!success]- Ответ
> > У таблицы есть журнал загруженных файлов (64 дня). Уже загруженный файл пропускается, пока не
> > указан `FORCE = TRUE`.

> [!question] 2. Что проверяет `dbt parse` и чего не проверяет?
> > [!success]- Ответ
> > Проверяет YAML, Jinja, `ref`/`source` и граф — без подключения. Не проверяет SQL диалекта и
> > существование таблиц: это делает только хранилище при `build`.

> [!question] 3. Почему перенос проекта затрагивает в основном staging?
> > [!success]- Ответ
> > В staging — имена и типы источников, а они зависят от того, как данные загружены в конкретное
> > хранилище. Витрины работают с уже нормальными именами из staging.
