# Лаба 06.1 · Dagster в compose: свой code location и загрузки как ассеты

**Модуль:** [06 · Оркестрация](../../README.md) · **Дата начала:** YYYY-MM-DD · **Статус:** ⬜

## Objective

Передать загрузки capstone из модуля 04 под управление Dagster: свой code location рядом с
учебным, загрузки bronze — ассеты на графе, адреса и ключи — только из окружения. Бизнес-смысл:
у сети появляется одно место, где видно, что и когда загружено.

## Key Terms

_(заполни своими словами)_

- **Ассет и материализация** —
- **Code location, code-сервер** —
- **Ресурс и `EnvVar`** —
- **Транслятор dlt** —

## Prerequisites

- Теория: [01 · Зачем оркестратор](../../theory/01_orchestration_basics.md),
  [02 · Как устроен Dagster](../../theory/02_dagster_architecture.md),
  [04 · dlt и dbt как ассеты](../../theory/04_dbt_dlt_lineage.md) (шаги 1–2)
- Лаба 04.6: `capstone/ingestion/` и `make ingest` работают
- `make up PROFILES="orchestration ingestion"`

## Tasks

### Task 1. Свой code location

**Expected result / Definition of Done:**
- Пакет `capstone/orchestration/` с модулем `definitions.py` (объект `Definitions`)
- Сервис `dagster-capstone` в `infra/docker/orchestration.yaml` и строка в
  `infra/docker/dagster/workspace.yaml`; webserver и daemon дожидаются его готовности
- `make ps` — сервис `healthy`; в UI → Deployment две code locations без ошибок
- `definitions validate` для твоего модуля — `Validation successful`; команда записана в README

**Steps:**
1. Разбери сервис `dagster-demo`: какие строки отвечают за код, окружение, проверку готовности
   (урок 02, шаг 3). Какие из них поменяются для capstone?
2. Подумай, нужен ли второму code-серверу другой порт, если это другой контейнер (модуль 00,
   урок 03).
3. Добавь сервис, строку в `workspace.yaml`, зависимости webserver и daemon; `make up
   PROFILES="orchestration"`.

### Task 2. Загрузки bronze как ассеты

**Expected result / Definition of Done:**
- Загрузки лаб 04.1, 04.3, 04.4 — ассеты (`@dlt_assets` или `@asset`, вызывающий твои функции;
  выбор обоснован в README)
- Ключи ассетов совпадают с именами таблиц bronze, ассеты сгруппированы (`group_name`)
- Материализация каждого ассета из UI проходит; в метаданных материализации — число строк
- Повторная материализация не создаёт дублей: запрос-сверка в `queries.sql` лабы

**Steps:**
1. Код загрузок не копируй — импортируй функции из `capstone/ingestion/`.
2. Что делает `run_all.py` из лабы 04.6 и что из этого теперь делает оркестратор?
3. Проверь граф: `make dagster ARGS="asset list"` показывает только демо — почему? Как вызвать
   CLI для своего code location (`docker compose … exec dagster-capstone …`)?

### Task 3. Ресурсы вместо адресов в коде

**Expected result / Definition of Done:**
- В коде `capstone/orchestration/` нет адресов, логинов и ключей: всё из ресурсов с `EnvVar`
  или из окружения, которое code-сервер унаследовал от workspace
- `grep -rnE "silo:9000|change-me|AKIA|password" capstone/orchestration` — пусто

## Результат

_(скриншот или описание графа, команды проверки, вывод сверки дублей)_

## Выводы и вопросы

- Что произойдёт с запусками capstone, если упадёт code-сервер демо? А если daemon?
