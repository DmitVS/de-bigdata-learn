# Лаба 05.1 · dbt-проект capstone: профиль, источники и staging

**Модуль:** [05 · Трансформации: dbt](../../README.md) · **Дата начала:** YYYY-MM-DD · **Статус:** ⬜

## Objective

Завести dbt-проект `capstone/transform`, подключить его к bronze в Iceberg и построить
staging-слой: по одной модели на каждую таблицу bronze, с нормальными именами и типами. Это
фундамент всех витрин курса.

## Key Terms

_(заполни своими словами)_

- **Модель, `ref`, `source`** —
- **Профиль и цель (target)** —
- **Staging-слой** —
- **Скомпилированный SQL** —

## Prerequisites

- Теория: [01 · dbt как проект](../../theory/01_dbt_project.md)
- Модуль 04: таблицы bronze загружены (`make ingest` из лабы 04.6)
- `make up`

## Tasks

### Task 1. Проект и профиль

**Expected result / Definition of Done:**
- `capstone/transform/` создан `dbt init … --skip-profile-setup`, пример `models/example`
  удалён
- `profiles.yml` в папке проекта: цель по умолчанию работает с файлом
  `/workspace/data/warehouse/freshretail.duckdb` и подключает каталог Iceberg; `dbt debug` — все
  проверки OK
- `dbt_project.yml`: материализации по папкам staging / intermediate / marts
- Папка `data/warehouse/` существует (DuckDB сам папки не создаёт); файл базы — вне git

**Steps:**
1. Профиль с `attach` — урок 01, шаг 3. Подумай, нужна ли тебе отдельная цель без каталога.
2. Где dbt ищет `profiles.yml` — урок 01, шаг 3.

### Task 2. Источники

**Expected result / Definition of Done:**
- `models/staging/_sources.yml` объявляет все таблицы bronze (продажи, справочники
  `retail_oltp`, промо, праздники) с описаниями
- `dbt ls --resource-type source` перечисляет их все
- Для каждой таблицы источника записан grain и естественный ключ (в описании)

### Task 3. Staging-модели

**Expected result / Definition of Done:**
- По одной модели `stg_<источник>__<сущность>` на таблицу bronze; `source()` встречается только
  в staging
- В staging: понятные имена колонок, `dt` → `DATE`, служебные колонки загрузки сохранены,
  дубли повторной доставки (если bronze их допускает, модуль 04) устранены
- `dbt build -s staging` — зелёный; `dbt show` для каждой модели даёт ожидаемые строки
- Число строк staging сверено с bronze (запросы — в README)

**Steps:**
1. Правила слоя — урок 01, шаг 5. Аргументы за и против view в staging — ловушка того же шага.
2. Если `dt` в bronze — строка, приведение — здесь, а не в marts.

## Результат

_(структура проекта, вывод `dbt build -s staging`)_

## Выводы и вопросы

- Что придётся поменять в проекте, если bronze переедет в другой namespace?
