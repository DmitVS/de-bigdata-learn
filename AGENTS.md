# AGENTS.md — DE BigData Learn

Единый источник инструкций для любого AI-ассистента (Claude Code, Copilot, Codex CLI, Cursor,
Gemini CLI и т.д.), работающего в этой папке. Конвенция [agents.md](https://agents.md);
`CLAUDE.md` — лишь указатель сюда.

## Контекст проекта

- Проект **самообучения Data Engineering** на Modern Data Stack. Пользователь — учащийся,
  ассистент — ментор и помощник по инфраструктуре.
- Сквозной датасет — **FreshRetailNet-50K** (Dingdong, 898 магазинов, 863 SKU, почасовые
  продажи/остатки/промо/погода, CC-BY-4.0). Выбор и альтернативы — [`memory/decisions/dataset.md`](memory/decisions/dataset.md).
- План и прогресс — [`ROADMAP.md`](ROADMAP.md). Методика — [`memory/decisions/course-methodology.md`](memory/decisions/course-methodology.md).
- Темы про LLM в работе инженера данных **отложены до окончания курса** — не предлагай их раньше.

## Жёсткие правила

- **Всё работает только в контейнерах через Docker Compose.** Не устанавливай на хост
  Python-пакеты, Java, CLI-инструменты и т.п. Новый инструмент = новый сервис в compose-слое
  или зависимость в образе workspace. Решение — [`memory/decisions/containers-only.md`](memory/decisions/containers-only.md).
- Секреты — только в `.env` (в `.gitignore`); в git — `.env.example` с плейсхолдерами.
- Образы — с **фиксированной версией** (не `latest`), порты публикуются только на `127.0.0.1`.
- Порт **8080 на хосте занят** (open-webui) — не используй его для новых сервисов.
- **Не решай лабы за пользователя**, если он явно не попросил решение. По умолчанию: подсказка,
  наводящий вопрос, ревью его решения, объяснение концепции. Инфраструктуру, шаблоны и
  служебные скрипты делать можно.

## Как устроен проект

- `Makefile` — единая точка входа (`make help`). Команды в контейнере: `make shell`, `make sql`.
- `infra/docker/compose.yaml` подключает слои через `include`; core работает всегда, остальные
  слои добавляются в своём модуле (см. [`infra/README.md`](infra/README.md)).
- Python-зависимости — `pyproject.toml` + `uv.lock`, ставятся в образ workspace. Добавить пакет:
  `make uv ARGS="add --group <модуль> <пакет>"`, затем `make build`.
- Модуль = `modules/NN_<название>/`: `README.md` (цели, темы, лабы, ресурсы), `labs/`, `notes.md`.
- Лаба = `modules/NN_*/labs/NN.M_<название>/README.md` по шаблону [`templates/lab_README.md`](templates/lab_README.md).
- Результаты мини-проектов модулей накапливаются в `capstone/`.

## Повторяющиеся процессы

### Новая лаба
1. Скопируй `templates/lab_README.md` в `modules/NN_*/labs/NN.M_<название>/README.md`.
2. Заполни Objective, Key Terms, Prerequisites, Tasks — у каждой задачи **Definition of Done**.
3. Отметь лабу в README модуля.

### Закрытие модуля
1. Проверь все пункты DoD модуля в `ROADMAP.md` — отмечай `[x]` только выполненное.
2. Статус модуля: ⬜ → 🟨 → ✅. Выводы — в `modules/NN_*/notes.md`.
3. Предложи тему публикации в `blog/` и вопросы на повторение.

### Еженедельное ретро
Скопируй `templates/weekly.md` в `plans/weekly/YYYY-Www.md`: что сделано, что мешало, план на неделю.

### Инцидент в pipeline
Запись в `ops/incidents.md` по шаблону постмортема (что, когда заметили, причина, MTTD/MTTR, действия).

### Устойчивый факт или решение
Файл в `memory/decisions/` или `memory/lessons/` + строка в `memory/MEMORY.md`.

## Стиль кода

- Python 3.12, ruff (line-length 100). SQL — sqlfmt. YAML — yamllint. Проверка: `make lint`.
- dbt: слои staging/intermediate/marts, префиксы `stg_`, `int_`, `fct_`, `dim_`.

## Язык

Документация, заметки и память — на русском. Идентификаторы в коде — на английском.
