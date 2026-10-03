#!/bin/sh
# CI, шаг test (модуль 12): pytest. Тесты Spark без кластера пропускаются (conftest модуля 07).
set -eu
uv run --frozen --all-groups pytest -q
