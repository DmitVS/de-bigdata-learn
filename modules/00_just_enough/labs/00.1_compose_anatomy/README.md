# Лаба 00.1 · Анатомия слоя core

**Модуль:** [00 · Just enough](../../README.md) · **Дата начала:** YYYY-MM-DD · **Статус:** ⬜

## Objective

Понять каждую строку [`infra/docker/core.yaml`](../../../../infra/docker/core.yaml) настолько,
чтобы суметь пересобрать слой с нуля и диагностировать любой его сбой. Всё дальнейшее в курсе
(Spark, Kafka, Dagster) — это новые сервисы в таких же compose-файлах.

## Key Terms

_(заполни своими словами по ходу лабы)_

- **Образ / контейнер / слой образа** —
- **Том (named volume) vs bind mount** —
- **Healthcheck** —
- **`depends_on` + `condition`** —
- **One-shot (init) контейнер** —
- **Сеть compose, встроенный DNS** —
- **Публикация порта (`ports`)** —
- **Vended credentials (STS)** —

## Prerequisites

- `make up` выполнен, `make check` — все OK
- Прочитано: [Compose file reference — services](https://docs.docker.com/reference/compose-file/services/),
  [Networking in Compose](https://docs.docker.com/compose/how-tos/networking/),
  [infra/README.md](../../../../infra/README.md)

## Tasks

### Task 1. Карта сервисов

**Expected result / Definition of Done:**
- Таблица ниже заполнена для всех 7 сервисов (включая одноразовые `*-init`, `*-migrate`)
- Mermaid-диаграмма зависимостей `depends_on` с подписями условий на стрелках

| Сервис | Образ | Зачем нужен | Порты (хост → контейнер) | Тома / монтирования | Зависит от (условие) | Долгоживущий или one-shot |
|---|---|---|---|---|---|---|
| postgres | | | | | | |
| … | | | | | | |

**Steps:**
1. Прочитай `core.yaml` и `compose.yaml` целиком.
2. Посмотри итоговую конфигурацию после подстановки переменных и `include`:
   `docker compose --env-file .env -f infra/docker/compose.yaml config` (осторожно: в выводе пароли — не коммить его).
3. Сверь с `make ps` — какие контейнеры в статусе `Exited (0)` и почему это нормально.

### Task 2. Порядок запуска

**Expected result / Definition of Done:**
- Письменно: предсказанный порядок старта всех сервисов и почему именно такой
- Предсказание сверено с реальностью (команды и вывод приложены)
- Ответы: чем `service_healthy` отличается от `service_completed_successfully`? Что будет, если у
  `lakekeeper` убрать зависимость от `lakekeeper-migrate`? Зачем `make up` использует `--wait`?

**Steps:**
1. Запиши предсказание.
2. `make down`, затем в одном терминале `docker events --filter label=com.docker.compose.project=debd`,
   в другом — `make up`. Сравни.

<details><summary>Подсказка</summary>

Смотри на события `start`, `health_status`, `die` и их порядок во времени.
</details>

### Task 3. Сети и DNS

**Expected result / Definition of Done:**
- Выполнены и приложены: из `make shell` — `getent hosts silo lakekeeper postgres`; с хоста —
  `curl -s localhost:9000` и `curl -s silo:9000`
- Ответы: почему внутри контейнера работает `silo:9000`, а на хосте — нет? Почему в `ports`
  указан `127.0.0.1:`, и что изменится, если его убрать? Зачем в `core.yaml` явная подсеть?
- Ответ: откуда `workspace` берёт S3-ключи, когда пишет Iceberg-таблицу — из своих `AWS_*`
  переменных или от каталога? Как это проверить?

<details><summary>Подсказка к последнему вопросу</summary>

Посмотри поля `sts-enabled` и `storage-credential` в `infra/docker/lakekeeper/init.sh` и раздел
«Vended credentials» в документации Lakekeeper. Эксперимент: временно убери `AWS_*` из окружения
одного процесса (`env -u AWS_ACCESS_KEY_ID -u AWS_SECRET_ACCESS_KEY python scripts/check_stack.py`).
</details>

### Task 4. Состояние и тома

**Expected result / Definition of Done:**
- Эксперимент: создал бакет `scratch` в консоли Silo (http://localhost:9001) → `make restart` → бакет на месте
- Ответы: где физически лежат данные Postgres и Silo (`docker volume inspect`)? Чем `make down`
  отличается от `make clean`? Почему `postgres/init/01-databases.sql` выполняется только один раз?
  А `lakekeeper/init.sh` — при каждом `make up`, и почему это безопасно?
- Ответ: почему данные датасета (`data/`) переживут `make clean`, а бакеты — нет?

### Task 5. Образ workspace

**Expected result / Definition of Done:**
- Ответы с опорой на [`Dockerfile`](../../../../infra/docker/workspace/Dockerfile) и `docker history debd/workspace:local`:
  1. Почему `COPY pyproject.toml uv.lock` и `uv sync` идут до монтирования кода, а не после?
  2. Почему venv в `/opt/venv`, а не в `/workspace/.venv`?
  3. Зачем аргументы `UID`/`GID`? Что будет с правами на файлы в `data/` без них?
  4. Какой слой образа самый тяжёлый и почему образ весит ~2,4 ГБ?
- Эксперимент: добавил пакет (например, `rich`) через `make uv ARGS="add --group dev rich"`,
  пересобрал `make build`, убедился, что он доступен в `make shell`, откатил изменения (`git restore`)

## Результат

_(таблица, диаграмма, ответы, ключевые выводы)_

## Выводы и вопросы

- 

По итогам лабы — шпаргалка [`cheatsheets/docker-compose.md`](../../../../cheatsheets/) своими словами (пункт DoD модуля).
