---
type: theory
module: "11"
topic: 4
labs: ["11.3"]
tasks: ["1", "2", "3"]
time: "~90 мин"
tags: [access-control, rbac, masking, row-level-security, trino, postgres, ethics]
---

# 04 · Доступы: кто что видит, маскирование и ответственность инженера

> [!info] Урок одной фразой
> Склад сети открыт не всем одинаково. Менеджер города заходит только в свой зал (фильтр
> строк). Партнёр-поставщик видит полки, но цены на них заклеены (маскирование колонок).
> Охранник проверяет пропуск у каждой двери: в Trino — правила в файле, в Postgres — роли и
> политики. А инженер решает, какие двери вообще ставить, — это уже вопрос этики, а не только
> закона.

> [!todo] Чек-лист: после урока ты сможешь
> - [ ] объяснить RBAC, принцип наименьших привилегий, классификацию данных;
> - [ ] описать правила доступа Trino: права на таблицу, маску колонки, фильтр строк;
> - [ ] настроить в Postgres роль, права на колонки и row-level security;
> - [ ] предсказать, что увидит пользователь без политики, и найти «утечки» через имена и метаданные;
> - [ ] объяснить, зачем инженеру этика данных, на примерах из нашего датасета.

**Нужно для:** лаба [11.3](../labs/11.3_access_control/README.md).
**Карта урока:** [access-control.canvas](../maps/access-control.canvas).

---

## Шаг 0. Азбука

| Понятие | В аналогии «склад с пропусками» | Подробнее |
|---|---|---|
| Аутентификация | Проверка, что ты — это ты (пропуск с фото) | [управление доступом](../../../glossary/access-control.md) |
| Авторизация | Решение, куда пускать этот пропуск | [управление доступом](../../../glossary/access-control.md) |
| RBAC, роль | Права выдают должности, а не человеку | [управление доступом](../../../glossary/access-control.md) |
| Наименьшие привилегии | Пропуск только в нужные залы | [управление доступом](../../../glossary/access-control.md) |
| Маскирование колонки | Цены заклеены, полки видны | [маскирование и RLS](../../../glossary/data-masking-rls.md) |
| Фильтр строк, RLS | Пускают только в свой зал | [маскирование и RLS](../../../glossary/data-masking-rls.md) |
| Классификация, PII | Ярлык «осторожно» на коробке | [классификация данных](../../../glossary/data-classification.md) |

---

## Шаг 1. Зачем ограничивать доступ к аналитическим данным

**Проблема.** Витрины строились «для всех»: дашборд сети видит каждый. Но у бизнеса другие
правила. Продажи отдельного магазина — коммерческая тайна; менеджер города должен видеть свой
город, а не соседний; внешний партнёр — тренды, но не выручку. Если витрина открыта целиком,
остаётся либо не пускать людей вовсе, либо копировать витрину под каждого.

**Как устроено.** Доступ проверяется в два шага:

1. **Аутентификация** — кто это. Пароль, токен, SSO. У учебного Trino её нет: пользователь
   называет себя сам (`--user partner`). В проде так нельзя.
2. **Авторизация** — что ему можно. Права выдают **ролям** (RBAC): «менеджер города»,
   «партнёр», «аналитик». Человек получает роль, а не набор прав по одному.

Уровни детализации прав:

| Уровень | Пример | Где у нас |
|---|---|---|
| каталог / база | партнёр не видит `postgresql` | Trino: `catalogs`; Postgres: `CONNECT` |
| схема | только `governance_demo` | Trino: `schemas`; Postgres: `USAGE` |
| таблица | только витрина, не staging | Trino: `tables`; Postgres: `GRANT SELECT` |
| колонка | всё, кроме `sales` | Trino: маска; Postgres: `GRANT SELECT (колонки)` |
| строка | только город 0 | Trino: `filter`; Postgres: row-level security |

**Что из этого следует.** Принцип **наименьших привилегий**: роль получает минимум, нужный для
работы. Права на колонки и строки позволяют держать одну витрину для всех, а не копию под каждую
роль.

---

## Шаг 2. Правила доступа в Trino

**Проблема.** Trino видит все каталоги: Iceberg, учётную систему, ClickHouse. Через него
пользователь дотянется до любых данных. Значит, правила должны стоять на входе в Trino.

**Как устроено.** Trino подключает **контроль доступа** плагином. Самый простой — правила в файле
(`access-control.name=file`). У нас: `infra/docker/trino/access-control.properties` и
`rules.json`; файл перечитывается каждые 10 с, перезапуск не нужен.

```json
{
  "tables": [
    {
      "user": "partner",                                         ①
      "catalog": "iceberg", "schema": "governance_demo",
      "table": "mart_city_oos_daily",
      "privileges": ["SELECT"],
      "columns": [{"name": "sales", "mask": "CAST(NULL AS double)"}]   ②
    },
    {
      "user": "city_manager_0",
      "catalog": "iceberg", "schema": "governance_demo",
      "table": "mart_city_oos_daily",
      "privileges": ["SELECT"],
      "filter": "city_id = 0"                                    ③
    },
    {"user": "partner|city_manager_0", "privileges": []},       ④
    {"privileges": ["SELECT", "INSERT", "DELETE", "UPDATE", "OWNERSHIP"]}   ⑤
  ]
}
```

| Метка | Что важно |
|---|---|
| ① | `user` — регулярное выражение по имени; есть также `role` и `group` |
| ② | маска — SQL-выражение того же типа, что колонка; запрос получает его вместо значения |
| ③ | фильтр — условие `WHERE`, которое Trino добавляет к каждому запросу пользователя |
| ④ | правила проверяются **сверху вниз до первого совпадения**: для остальных таблиц у этих пользователей прав нет |
| ⑤ | правило для всех прочих: Superset, Evidence, dbt работают как раньше |

**Что из этого следует.** Маска и фильтр работают для любого клиента Trino — Superset, Evidence,
Python, — потому что их применяет движок. Пользователь не может их обойти, пока ходит через Trino.

> [!example]- Попробуй сам: три пользователя — три ответа
> ```bash
> make up PROFILES="serving"
> make trino ARGS="--user dbt --execute \"SELECT count(*), count(DISTINCT city_id), round(sum(sales)) FROM iceberg.governance_demo.mart_city_oos_daily\""
> make trino ARGS="--user partner --execute \"SELECT count(*), count(DISTINCT city_id), round(sum(sales)) FROM iceberg.governance_demo.mart_city_oos_daily\""
> make trino ARGS="--user city_manager_0 --execute \"SELECT count(*), count(DISTINCT city_id), round(sum(sales)) FROM iceberg.governance_demo.mart_city_oos_daily\""
> make trino ARGS="--user partner --execute \"SELECT count(*) FROM iceberg.serving_demo.fct_sales_daily\""
> ```
> **Увидишь:** `"1746","18","4911229.0"`; у партнёра — `"1746","18",""`; у менеджера —
> `"97","1","2594504.0"`; последняя команда — `Access Denied: Cannot select from table
> iceberg.serving_demo.fct_sales_daily`.
> **Почему:** у партнёра `sales` заменена на `NULL`, у менеджера к запросу добавлен
> `WHERE city_id = 0`, а все прочие таблицы закрыты правилом ④.
> Таблица `governance_demo.mart_city_oos_daily` строится в уроке 01 (шаг 4).

> [!warning] Ловушка
> Проверяй, что видно в метаданных, а не только в данных. На стеке партнёр получает `Access
> Denied` на чтение staging, но `SHOW TABLES FROM iceberg.governance_demo` показывает ему все
> четыре таблицы. Имена таблиц и колонок тоже могут быть секретом.

---

## Шаг 3. Доступ в Postgres: роли, колонки, row-level security

**Проблема.** Не все ходят через Trino. Приложение, Debezium (модуль 08), dlt (модуль 04)
подключаются к `retail_oltp` напрямую. Значит, правила нужны и в самой базе.

**Как устроено.** В Postgres всё строится на **ролях**:

```sql
CREATE ROLE city_manager_0 NOLOGIN;                                 -- ① роль-должность
GRANT USAGE ON SCHEMA serving_demo TO city_manager_0;               -- ② вход в схему
GRANT SELECT ON serving_demo.stores TO city_manager_0;              -- ③ таблица
GRANT SELECT (store_id, city_id) ON serving_demo.stores TO partner; -- ④ только колонки
ALTER TABLE serving_demo.stores ENABLE ROW LEVEL SECURITY;          -- ⑤ включить RLS
CREATE POLICY city0 ON serving_demo.stores FOR SELECT
    TO city_manager_0 USING (city_id = 0);                          -- ⑥ политика строк
```

| Метка | Что важно |
|---|---|
| ① | роль без `LOGIN` — должность; людям дают `LOGIN`-роли и `GRANT city_manager_0 TO ivan` |
| ② | без `USAGE` на схему таблица недоступна, даже если на неё есть `SELECT` |
| ④ | `SELECT *` у партнёра упадёт: `permission denied for table stores`; нужно перечислить колонки |
| ⑤ | после включения RLS роль **без политики видит 0 строк — без ошибки** |
| ⑥ | `USING` — условие, которое Postgres добавляет к запросам этой роли |

Владелец таблицы и суперпользователь RLS обходят. Чтобы политика действовала и на владельца,
нужна `ALTER TABLE … FORCE ROW LEVEL SECURITY`.

**Что из этого следует.** RLS опасен тихим отказом: отчёт с нулями вместо ошибки. Проверяй
каждую роль запросом `count(*)` после включения политик.

> [!example]- Попробуй сам: роль менеджера и роль без политики
> ```bash
> docker compose --env-file .env -f infra/docker/compose.yaml exec postgres psql -U de -d retail_oltp
> ```
> ```sql
> CREATE ROLE zz_mgr NOLOGIN; CREATE ROLE zz_partner NOLOGIN;
> GRANT USAGE ON SCHEMA serving_demo TO zz_mgr, zz_partner;
> GRANT SELECT ON serving_demo.stores TO zz_mgr;
> GRANT SELECT (store_id, city_id) ON serving_demo.stores TO zz_partner;
> ALTER TABLE serving_demo.stores ENABLE ROW LEVEL SECURITY;
> CREATE POLICY zz_city0 ON serving_demo.stores FOR SELECT TO zz_mgr USING (city_id = 0);
> SET ROLE zz_mgr; SELECT count(*) FROM serving_demo.stores; RESET ROLE;
> SET ROLE zz_partner; SELECT count(store_id) FROM serving_demo.stores;
> SELECT status FROM serving_demo.stores LIMIT 1; RESET ROLE;
> SELECT count(*) FROM serving_demo.stores;
> DROP POLICY zz_city0 ON serving_demo.stores;
> ALTER TABLE serving_demo.stores DISABLE ROW LEVEL SECURITY;
> REVOKE ALL ON serving_demo.stores FROM zz_mgr, zz_partner;
> REVOKE ALL ON SCHEMA serving_demo FROM zz_mgr, zz_partner;
> DROP ROLE zz_mgr; DROP ROLE zz_partner;
> \q
> ```
> **Увидишь:** у менеджера — `290`; у партнёра — `0` и затем `permission denied for table
> stores`; у тебя (владельца) — `898`.
> **Почему:** у партнёра нет политики RLS — он видит 0 строк; колонки `status` нет в его правах.
> Владелец таблицы RLS обходит.

---

## Шаг 4. Классификация: что именно защищать

**Проблема.** Правила пишут для конкретных колонок. Но в 40 таблицах никто не помнит, где лежат
продажи по магазинам, а где — телефоны клиентов. Нужна разметка.

**Как устроено.** **Классификация** — метки на колонках по чувствительности: `PII` (персональные
данные), `commercial` (коммерческая тайна), `public`. В каталоге (урок 01) это теги
`PII.Sensitive`, `PII.NonSensitive` и свои классификации. Метка проходит по lineage колонок
(урок 02): если `sales` помечена в источнике, видно, в каких витринах она оказалась.

В нашем датасете **нет персональных данных**: магазины, товары и города закодированы числами.
Чувствительные данные у нас — коммерческие: продажи отдельного магазина и товара. В проекте
`dbt_governance` колонка `sales` помечена `meta: sensitivity: commercial`.

**Что из этого следует.** Порядок работы: классифицировать → решить политику для каждой метки →
реализовать правила в движках (Trino, Postgres) → проверять запросами от имени ролей.

---

## Шаг 5. Этика: что инженер решает сам

**Проблема.** Закон говорит, что нельзя. Но многие решения закон не регулирует: какие данные
собирать, как долго хранить, кому давать детализацию. Клеппман (гл. 12, *Doing the Right Thing*)
напоминает: эти решения принимает инженер, даже если он думает, что «просто строит пайплайн».

**Как устроено.** Вопросы, которые стоит задавать на нашем примере:

| Вопрос | Пример у нас |
|---|---|
| Нужна ли такая детализация? | почасовые продажи по магазину партнёру не нужны — хватит города за день |
| Можно ли восстановить скрытое? | маска на `sales`, но открыты продажи всех остальных товаров и итог — разность выдаст скрытое число |
| Сколько хранить? | сырые события дольше, чем нужно для витрин, — лишний риск утечки |
| Кто отвечает? | у каждой таблицы — владелец в каталоге (урок 01), он решает о доступе |

**Что из этого следует.** Маскирование и фильтры — инструменты. Решение «что показывать» — за
людьми, и инженер в нём участвует: предлагает агрегировать раньше, хранить меньше, давать меньше.

---

## Сборка целиком

Запрос партнёра через Superset к витрине:

```mermaid
sequenceDiagram
    autonumber
    participant P as партнёр
    participant SS as Superset
    participant T as Trino (координатор)
    participant R as rules.json
    participant I as Iceberg
    P->>SS: открыл чарт «Продажи по городам»
    SS->>T: SELECT city_id, sum(sales) … (user = partner)
    T->>R: правило для partner и mart_city_oos_daily
    R-->>T: SELECT разрешён; маска sales = NULL
    T->>I: чтение витрины
    T-->>SS: суммы = NULL
    SS-->>P: пустой график продаж, доли без товара видны
```

| Шаг | Если ошибиться | Симптом |
|---|---|---|
| 2 | Superset ходит в Trino одним техническим пользователем | правила по людям не работают — нужен проброс пользователя (impersonation) |
| 4 | маска не того типа | ошибка запроса у партнёра |
| 4 | правило-«ловушка» ④ забыто | партнёр читает все таблицы |

## Шпаргалка

| Хочу | Как |
|---|---|
| Включить правила Trino | `access-control.properties`: `access-control.name=file`, `security.config-file=…` |
| Скрыть колонку в Trino | `"columns": [{"name": "c", "mask": "CAST(NULL AS тип)"}]` |
| Фильтр строк в Trino | `"filter": "city_id = 0"` |
| Запрос от имени пользователя | `make trino ARGS="--user partner --execute \"…\""` |
| Роль в Postgres | `CREATE ROLE r NOLOGIN; GRANT USAGE ON SCHEMA s TO r; GRANT SELECT ON t TO r` |
| Права на колонки | `GRANT SELECT (a, b) ON t TO r` |
| RLS | `ALTER TABLE t ENABLE ROW LEVEL SECURITY; CREATE POLICY p ON t FOR SELECT TO r USING (…)` |
| Проверить роль | `SET ROLE r; SELECT …; RESET ROLE;` |

## Типичные ошибки

| Симптом | Причина | Как проверить | Как чинить |
|---|---|---|---|
| Роль видит 0 строк без ошибки | RLS включён, политики для роли нет | `SELECT * FROM pg_policies` | политика для роли |
| `permission denied for table` при `SELECT *` | права только на часть колонок | `\dp таблица` | перечислить разрешённые колонки |
| Владелец видит всё вопреки политике | владелец обходит RLS | — | `FORCE ROW LEVEL SECURITY` |
| В Trino у всех `Access Denied` | нет правила для прочих пользователей | порядок правил | правило-«для всех» последним |
| Правку `rules.json` не видно | ждать до 10 с | `security.refresh-period` | подождать или перезапустить Trino |

## Проверь себя

Карточки — в [flashcards.md](../flashcards.md).

> [!question] 1. Включили RLS на `stores`, создали политику только для менеджеров. Что увидит отчёт аналитика, который работает под своей ролью?
> > [!success]- Ответ
> > Ноль строк и никакой ошибки: роль без политики при включённом RLS не видит ничего. Нужна
> > политика для аналитиков (например, `USING (true)`).

> [!question] 2. Партнёру замаскировали `sales`. Как он всё равно может узнать продажи города 0?
> > [!success]- Ответ
> > Если открыта другая таблица с теми же продажами (staging, итог по сети и по другим
> > городам) — вычитанием. Поэтому у партнёра закрыто всё, кроме одной витрины (правило ④), а
> > решение о детализации принимают по lineage колонки `sales`.

> [!question] 3. Почему маска в Trino надёжнее, чем фильтр в датасете Superset?
> > [!success]- Ответ
> > Маску применяет движок для любого клиента. Фильтр Superset обходится через SQL Lab, Python
> > или Evidence.

> [!question] 4. В нашем датасете нет PII. Значит, governance доступа не нужен?
> > [!success]- Ответ
> > Нужен: продажи магазинов и товаров — коммерческая тайна, у городов — свои менеджеры. Плюс
> > в capstone появятся данные учётной системы, и разметку лучше делать с первого дня.
