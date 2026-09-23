---
name: containers-only
description: Все инструменты курса работают только в контейнерах через Docker Compose; на хосте только docker и make
metadata:
  type: decision
---

Решение пользователя от 2026-09-23: **все инструменты — только в контейнерах, развёртывание — docker compose**.

- Python-инструменты (dbt, dlt, DuckDB, Polars, PyIceberg, Jupyter, линтеры) — в образе
  `workspace` (`infra/docker/workspace/Dockerfile`), зависимости в `pyproject.toml` + `uv.lock`.
- uv для правки зависимостей запускается одноразовым контейнером (`make uv`, `make lock`).
- Серверные компоненты — сервисы compose-слоёв в `infra/docker/`.
- На хост ничего не ставим (uv, поставленный на хост до этого решения, удалён; Java не нужна).
- Следствие: pre-commit как git-хук на хосте не используем; проверки — `make lint` в контейнере,
  автоматизация — CI в модуле 12.
