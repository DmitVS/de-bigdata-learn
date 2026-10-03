#!/bin/sh
# CI, шаг lint (модуль 12): те же проверки, что make lint. Запуск из корня курса.
set -eu
uv run --frozen --only-group dev ruff check .
uv run --frozen --only-group dev ruff format --check .
uv run --frozen --only-group dev sqlfmt --check .
uv run --frozen --only-group dev yamllint -s infra
