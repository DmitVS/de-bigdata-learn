---
type: theory
module: "05"
topic: 6
labs: ["05.6"]
tasks: ["1", "2", "3"]
time: "~80 мин"
tags: [sqlmesh, dbt, virtual-environments, plan-apply]
---

# 06 · SQLMesh: другой взгляд на трансформации

> [!info] Урок одной фразой
> В dbt новое меню готовят прямо на раздаче: пересобрал модель — и все сразу едят новое. В
> SQLMesh у кухни есть тестовый зал (dev-окружение): новое блюдо готовят и пробуют там, а когда
> оно одобрено, просто вешают на раздачу табличку «теперь подаём это» — без повторной готовки.
> Шеф заранее говорит, какие блюда придётся переделать из-за изменения (план).

> [!todo] Чек-лист: после урока ты сможешь
> - [ ] описать модель SQLMesh блоком `MODEL` и выбрать её вид (`VIEW`, `FULL`, `INCREMENTAL_BY_TIME_RANGE`);
> - [ ] объяснить виртуальный слой: физические таблицы-версии и представления окружений;
> - [ ] прочитать план: прямые и косвенные изменения, Breaking и Non-breaking, что пересчитывается;
> - [ ] сделать изменение в dev, сравнить с prod (`table_diff`) и выкатить без пересчёта;
> - [ ] сравнить SQLMesh и dbt по конкретным пунктам (лаба 05.6).

**Нужно для:** лабы [05.6](../labs/05.6_sqlmesh/README.md).
**Карта урока:** [sqlmesh.canvas](../maps/sqlmesh.canvas).

---

## Шаг 0. Азбука: тестовый зал и табличка на раздаче

Учебный проект — [`demo_sqlmesh/`](../demo_sqlmesh/): та же погода по городам, что в
`demo/` на dbt, чтобы сравнивать одно и то же. SQLMesh 0.228 стоит в workspace (группа
зависимостей `transform`).

| В SQLMesh | В аналогии «кухня» | Подробнее |
|---|---|---|
| Модель с блоком `MODEL` | Рецепт с паспортом | [SQLMesh](../../../glossary/sqlmesh.md) |
| Окружение (prod, dev) | Основной зал / тестовый зал | [SQLMesh](../../../glossary/sqlmesh.md) |
| Физический слой | Кастрюли с готовыми версиями блюд | [SQLMesh](../../../glossary/sqlmesh.md) |
| Виртуальный слой | Табличка на раздаче «подаём из этой кастрюли» | [SQLMesh](../../../glossary/sqlmesh.md) |
| План (plan) | Список «что переделать» до начала работы | [SQLMesh](../../../glossary/sqlmesh.md) |
| Breaking / Non-breaking | Меняет ли изменение то, что уже едят потребители | [SQLMesh](../../../glossary/sqlmesh.md) |
| Аудит (audit) | Дегустация, без которой блюдо не выйдет | [тесты dbt](../../../glossary/dbt-tests.md) |

---

## Шаг 1. Модель SQLMesh

**Проблема.** В dbt настройки модели — в Jinja `config()` и в YAML, а SQL — шаблон. SQLMesh
понимает SQL **сам** (парсер sqlglot): видит колонки, зависимости, типы без запуска.

**Как устроено.** Модель — `.sql` с блоком `MODEL` в начале:

```sql
MODEL (
  name weather.city_weather_daily,          -- ① схема.имя: зависимости — по именам в FROM
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column weather_date                -- ② инкремент по времени встроен
  ),
  cron '@daily',                            -- ③ как часто появляется новый интервал
  grain (city_id, weather_date),            -- ④ ключ строки
  audits (not_null(columns := (city_id, weather_date)))   -- ⑤ блокирующие проверки
);

SELECT city_id, weather_date, AVG(precipitation) AS precipitation, COUNT(*) AS stores
FROM weather.stg_weather                     -- без ref(): SQLMesh сам разбирает зависимости
WHERE weather_date BETWEEN @start_date AND @end_date   -- ⑥ интервал подставит SQLMesh
GROUP BY city_id, weather_date
```

| Метка | Сравнение с dbt |
|---|---|
| ① | вместо `ref()` — обычное имя таблицы; граф строится разбором SQL |
| ② | аналог incremental/microbatch, но SQLMesh **помнит, какие интервалы построены** (таблица `_intervals`) |
| ③ | расписание — часть модели |
| ④ | grain объявлен, по нему работают `table_diff` и проверки |
| ⑤ | аудит упал → модель не публикуется (в dbt тест — после построения) |
| ⑥ | вместо `is_incremental()` — макропеременные интервала |

Виды моделей: `VIEW`, `FULL` (таблица целиком), `INCREMENTAL_BY_TIME_RANGE`,
`INCREMENTAL_BY_UNIQUE_KEY`, `SCD_TYPE_2`, `SEED`.

---

## Шаг 2. Физический и виртуальный слои

**Проблема.** В dbt изменение модели пересобирает таблицу **на месте**: проверить новую версию
рядом со старой можно, только собрав её в другой схеме — и потом собрать ещё раз в prod.

**Как устроено.** SQLMesh хранит каждую **версию** модели отдельной физической таблицей в схеме
`sqlmesh__<схема>`: имя включает отпечаток (fingerprint) кода модели. А то, что видят
пользователи, — **представления**:

```
weather.city_weather_daily        → VIEW → sqlmesh__weather.weather__city_weather_daily__3358357567
weather__dev.city_weather_daily   → VIEW → sqlmesh__weather.weather__city_weather_daily__<новая версия>
```

Окружение `dev` — набор представлений в схеме `weather__dev`. Модели, которые не менялись, в
dev указывают на **те же** физические таблицы, что в prod: копировать ничего не нужно.

**Что из этого следует.** Выкатка в prod — это **переключение представлений** на уже
построенные и проверенные в dev таблицы. Мы проверили: после `sqlmesh plan dev` повторный
`sqlmesh plan` в prod сообщает `No physical layer updates to perform` и только обновляет
виртуальный слой.

---

## Шаг 3. План: что изменилось и что пересчитать

**Проблема.** Изменил модель — что придётся пересчитать? В dbt ответ даёт селектор
`state:modified+` (урок 04), но пересчитываются **все** потомки.

**Как устроено.** `sqlmesh plan [окружение]` сравнивает файлы проекта с окружением и
**классифицирует** каждое изменение:

| Класс | Что значит | Что пересчитывается |
|---|---|---|
| **Directly Modified** | изменён код модели | сама модель |
| **Indirectly Modified** | изменился предок | зависит от класса |
| **Non-breaking** | добавлена колонка; существующие колонки потомков не меняются | потомки — нет |
| **Breaking** | изменились строки или значения существующих колонок (фильтр, формула) | все потомки |

Классификацию SQLMesh делает **разбором SQL**: добавить колонку в SELECT — безопасно,
поменять WHERE — нет. Если он не уверен, спрашивает (или берёт настройку проекта).

> [!example]- Попробуй сам: два изменения в dev и сравнение с prod
> В `make shell`:
> ```bash
> cd modules/05_transformation_dbt/demo_sqlmesh
> sqlmesh plan --auto-apply                                  # prod: построить всё
> cp models/city_weather_daily.sql /tmp/cwd.orig.sql
> # 1) новая колонка
> sed -i 's/  COUNT(\*) AS stores/  COUNT(*) AS stores,\n  MAX(precipitation) AS max_precipitation/' models/city_weather_daily.sql
> sqlmesh plan dev --auto-apply 2>&1 | grep -E "Breaking|Non-breaking|backfill"
> # 2) фильтр строк
> sed -i 's/FROM weather.stg_weather/FROM weather.stg_weather\nWHERE precipitation IS NOT NULL AND/' models/city_weather_daily.sql
> sed -i 's/^WHERE weather_date BETWEEN/  weather_date BETWEEN/' models/city_weather_daily.sql
> sqlmesh plan dev --auto-apply 2>&1 | grep -E "Breaking|Non-breaking|backfill"
> sqlmesh table_diff prod:dev weather.city_weather_daily
> cp /tmp/cwd.orig.sql models/city_weather_daily.sql         # вернуть модель
> sqlmesh invalidate dev && sqlmesh janitor                  # убрать dev-окружение
> sqlmesh plan                                               # prod не менялся
> ```
> **Увидишь:** первое изменение — `city_weather_daily (Non-breaking)`, потомок
> `city_rainy_days (Indirect Non-breaking)`, пересчёт только изменённой модели. Второе —
> `(Breaking)` и `(Indirect Breaking)`: пересчитываются обе. `table_diff` показывает
> `Added Columns: max_precipitation (DOUBLE)` и сравнение строк по grain. В конце — `No changes
> to plan: project files match the prod environment`.
> **Почему:** колонка не меняет то, что потомок уже читает; фильтр меняет строки, значит меняет
> и результат потомка.

> [!warning] Ловушка: интервалы «до сегодня»
> Как и microbatch в dbt (урок 02), инкрементальная модель SQLMesh строит интервалы от `start`
> до текущей даты: в плане видно `[2024-03-28 - 2026-09-30]`. Без `batch_size` это один запрос,
> поэтому быстро. С `batch_size` на исторических данных получатся сотни пустых пачек. В prod-
> плане нельзя задать `--end` без restatement — данные сами должны «кончаться».

---

## Шаг 4. Тесты и аудиты

**Проблема.** Где в SQLMesh проверки логики и данных?

**Как устроено.** Две вещи, как в dbt:

- **Тест** (`tests/*.yaml`) — как unit-тест dbt: входы-фикстуры и ожидаемый выход модели.
  `sqlmesh test`.
- **Аудит** — как тест данных dbt, но **блокирующий**: выполняется после построения версии и
  до того, как окружение на неё переключится. Упал аудит — пользователи продолжают видеть
  старую версию.

```yaml
# tests/test_city_rainy_days.yaml
test_rainy_day_threshold:
  model: weather.city_rainy_days
  inputs:
    weather.city_weather_daily:
      rows:
        - {city_id: 0, weather_date: 2024-04-02, precipitation: 10.0, avg_temperature: 12.0, stores: 1}
  outputs:
    query:
      rows:
        - {city_id: 0, days: 1, rainy_days: 1, avg_temperature: 12.0}
```

`sqlmesh render модель` показывает итоговый SQL с подставленными физическими таблицами — аналог
`dbt compile`.

---

## Шаг 5. dbt или SQLMesh

| Пункт | dbt | SQLMesh |
|---|---|---|
| Зависимости | `ref()` / `source()` в Jinja | разбор SQL, обычные имена таблиц |
| Шаблоны | Jinja | макросы SQLMesh (`@…`) и Python; понимает SQL семантически |
| Инкремент | `is_incremental()`, microbatch; что построено, dbt не помнит | интервалы помнит сам, догоняет пропуски |
| Dev / prod | разные схемы, каждая собирается отдельно | виртуальные окружения: выкатка без пересчёта |
| Последствия изменения | `state:modified+` — все потомки | классификация Breaking / Non-breaking |
| Проверки | тесты после построения (могут не блокировать) | аудиты блокируют публикацию |
| Column-level lineage | нет в dbt Core | есть (разбор SQL) |
| Экосистема | огромная: пакеты, адаптеры, вакансии, Elementary, каталоги | меньше; умеет запускать dbt-проекты |
| Порог входа | ниже | выше: состояние, окружения, план |

**Что из этого следует.** dbt — стандарт рынка (модуль 01: частотность навыков в вакансиях),
поэтому capstone строится на dbt. SQLMesh полезно знать как ответ на слабые места dbt:
дорогие пересборки окружений и «слепой» инкремент.

---

## Сборка целиком

Изменение модели в SQLMesh от правки до prod:

```mermaid
sequenceDiagram
    autonumber
    participant U as Ты
    participant P as sqlmesh plan dev
    participant PH as Физический слой
    participant V as Виртуальный слой
    U->>P: правка city_weather_daily
    P->>P: отпечаток изменился → новая версия; классификация Non-breaking
    P->>PH: построить новую версию таблицы, аудиты
    P->>V: weather__dev.* → новая версия
    U->>P: sqlmesh plan (prod)
    P->>V: weather.* → та же версия (No physical layer updates)
```

| Шаг | Если сломается | Симптом |
|---|---|---|
| 2 | классификация не та | лишний или недостаточный пересчёт потомков |
| 3 | аудит упал | версия не опубликована, окружение указывает на старую |
| 5 | забыли выкатить | prod на старой версии, dev — на новой |

## Шпаргалка

| Хочу | Как |
|---|---|
| Построить / обновить prod | `sqlmesh plan --auto-apply` |
| Окружение для правки | `sqlmesh plan dev --auto-apply` |
| Сравнить окружения | `sqlmesh table_diff prod:dev модель` |
| Итоговый SQL | `sqlmesh render модель` |
| Выполнить запрос | `sqlmesh fetchdf "select …"` |
| Тесты | `sqlmesh test` |
| Убрать окружение | `sqlmesh invalidate dev && sqlmesh janitor` |

## Типичные ошибки

| Симптом | Причина | Как проверить | Как чинить |
|---|---|---|---|
| `start and end dates can't be set for a production plan` | `--end` в prod-плане | команда | убрать `--end` или restatement |
| Изменение классифицировано Breaking, хотя «безопасно» | меняются значения существующих колонок | диф в плане | так и есть: потомков надо пересчитать |
| В dev видны старые данные | не применён план (`--auto-apply` / подтверждение) | `sqlmesh plan dev` | применить |
| Схемы `sqlmesh__*` растут | старые версии не удалены | список таблиц | `sqlmesh janitor` |

## Проверь себя

Карточки — в [flashcards.md](../flashcards.md).

> [!question] 1. Почему выкатка из dev в prod в SQLMesh не пересчитывает данные?
> > [!success]- Ответ
> > Версия модели уже построена физической таблицей в dev и проверена аудитами. Prod —
> > представления, которые переключаются на ту же таблицу.

> [!question] 2. Добавление колонки — Non-breaking, изменение WHERE — Breaking. Почему?
> > [!success]- Ответ
> > Новая колонка не меняет строки и значения, которые читают потомки. WHERE меняет набор строк,
> > значит меняет результаты потомков, и их надо пересчитать.

> [!question] 3. Чем аудит SQLMesh отличается от теста данных dbt по последствиям?
> > [!success]- Ответ
> > Аудит выполняется до переключения окружения: если упал, пользователи видят прежнюю версию.
> > Тест dbt выполняется после того, как таблица уже заменена.
