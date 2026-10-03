#!/bin/sh
# CI, шаг dbt (модуль 12): сборка учебного dbt-проекта модуля 05 на DuckDB без стека.
#   1. Проект читает данные по пути /workspace/data/raw — как в контейнере workspace. В CI корень
#      курса связывается с /workspace символической ссылкой.
#   2. Датасет скачивается с Hugging Face (повторно — только изменившиеся файлы).
#   3. Slim CI: если есть состояние прода (STATE_DIR/manifest.json — manifest последней сборки
#      main), строятся только изменённые модели и их потомки, остальное берётся из прода (--defer).
#      Нет состояния — полная сборка.
# Переменные: STATE_DIR (по умолчанию ci_state), DBT_TARGET_DIR (по умолчанию target).
set -eu
ROOT=$(pwd)
STATE_DIR=${STATE_DIR:-$ROOT/ci_state}
if [ ! -e /workspace ]; then
  if [ "$(id -u)" = 0 ]; then ln -s "$ROOT" /workspace; else sudo ln -s "$ROOT" /workspace; fi
fi
uv run --frozen python datasets/download_freshretail.py
cd modules/05_transformation_dbt/demo
uv run --frozen dbt deps --quiet
if [ -f "$STATE_DIR/manifest.json" ]; then
  echo "slim CI: state:modified+ против $STATE_DIR"
  uv run --frozen dbt build --select state:modified+ --defer --state "$STATE_DIR"
else
  echo "полная сборка: нет $STATE_DIR/manifest.json"
  uv run --frozen dbt build
fi
uv run --frozen dbt docs generate
