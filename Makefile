# Единая точка входа. На хосте нужны только docker (с compose v2) и make.
# Все инструменты работают в контейнерах, см. infra/README.md.

COMPOSE  := docker compose --env-file .env -f infra/docker/compose.yaml
EXEC     := $(COMPOSE) exec workspace
UV_IMAGE := ghcr.io/astral-sh/uv:python3.12-bookworm-slim
CURL_IMAGE := curlimages/curl:8.22.0
# uv в одноразовом контейнере — для изменения зависимостей (pyproject.toml / uv.lock)
UV_RUN   := docker run --rm -u $$(id -u):$$(id -g) -v $(CURDIR):/w -w /w \
            -e UV_CACHE_DIR=/tmp/uv-cache $(UV_IMAGE) uv

.DEFAULT_GOAL := help
.PHONY: help init lock uv build up down restart ps logs shell sql check data lint fmt test obsidian clean dagster dagster-shell rpk flink-sql ch trino report om-token om-ingest spark-lineage tf precommit hooks ci video ste

help: ## Список команд
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-10s\033[0m %s\n",$$1,$$2}'

init: ## Создать .env из шаблона (UID/GID текущего пользователя)
	@test -f .env && echo ".env уже существует" || \
	  (sed -e "s/^HOST_UID=.*/HOST_UID=$$(id -u)/" -e "s/^HOST_GID=.*/HOST_GID=$$(id -g)/" \
	    .env.example > .env && echo ".env создан — при желании поменяй пароли")

lock: ## Пересобрать uv.lock после ручной правки pyproject.toml
	$(UV_RUN) lock

uv: ## Выполнить uv, напр.: make uv ARGS="add --group spark pyspark" (затем make build)
	$(UV_RUN) $(ARGS) $(if $(filter add remove,$(firstword $(ARGS))),--no-sync,)

build: ## Собрать образ workspace
	$(COMPOSE) build workspace

up: ## Поднять слой core (+ профили: make up PROFILES="spark streaming")
	$(COMPOSE) $(foreach p,$(PROFILES),--profile $(p)) up -d --wait

down: ## Остановить все контейнеры (данные в томах сохраняются)
	$(COMPOSE) --profile '*' down

restart: down up ## Перезапустить

ps: ## Статус контейнеров
	$(COMPOSE) --profile '*' ps -a

logs: ## Логи, напр.: make logs S=lakekeeper
	$(COMPOSE) --profile '*' logs -f --tail=200 $(S)

shell: ## Bash внутри workspace
	$(EXEC) bash

sql: ## DuckDB CLI внутри workspace
	$(EXEC) duckdb

dagster: ## Dagster CLI в code-сервере демо (модуль 06), напр.: make dagster ARGS="asset list"
	$(COMPOSE) exec dagster-demo dagster $(ARGS) $(if $(filter asset,$(firstword $(ARGS))),-m weather_orchestration.definitions,)

dagster-shell: ## Bash внутри code-сервера Dagster (модуль 06)
	$(COMPOSE) exec dagster-demo bash

rpk: ## CLI Redpanda (модуль 08), напр.: make rpk ARGS="topic list"
	$(COMPOSE) exec redpanda rpk $(ARGS)

flink-sql: ## Flink SQL-клиент (модуль 08); скрипт: make flink-sql ARGS="-f /workspace/…sql"
	$(COMPOSE) exec flink-jobmanager ./bin/sql-client.sh $(ARGS)

ch: ## ClickHouse-клиент (модуль 10), напр.: make ch ARGS="-q 'SELECT 1'"; файл: ARGS="--queries-file modules/…sql"
	$(COMPOSE) exec clickhouse clickhouse-client $(ARGS)

trino: ## Trino CLI (модуль 10), напр.: make trino ARGS="--execute 'SHOW CATALOGS'"
	$(COMPOSE) exec trino trino $(ARGS)

report: ## Собрать отчёт Evidence в build/ (модуль 10); папка — EVIDENCE_DIR=… (по умолчанию учебный отчёт)
	$(COMPOSE) --profile serving --profile evidence stop evidence
	$(COMPOSE) --profile serving --profile evidence run --rm --no-deps evidence sh -c "npm ci && npm run sources && npm run build"

om-token: ## OpenMetadata (модуль 11): токен бота в .env и сервис пайплайнов openlineage
	$(EXEC) python scripts/om_token.py

om-ingest: ## Сбор метаданных OpenMetadata (модуль 11): make om-ingest CFG=modules/…/x.yaml [CMD=ingest|profile]
	$(COMPOSE) --profile governance run --rm om-ingest $(or $(CMD),ingest) -c $(CFG)

spark-lineage: ## Задача Spark с агентом OpenLineage (модуль 11): make spark-lineage [JOB=modules/…py]
	$(COMPOSE) --profile governance run --rm spark-lineage $(or $(JOB),modules/11_governance/demo/spark_store_sales.py)

TF_DIR ?= modules/12_dataops_cicd/demo/terraform_local
TF_IMAGE := hashicorp/terraform:1.16.5
tf: ## Terraform в контейнере (модуль 12): make tf ARGS="plan" [TF_DIR=…]; ключи — из .env
	@set -a; . ./.env; set +a; docker run --rm -u $$(id -u):$$(id -g) --network debd_default \
	  -v $(CURDIR):/w -w /w/$(TF_DIR) -e HOME=/tmp -e TF_DATA_DIR=/w/data/.terraform/$(notdir $(TF_DIR)) \
	  -e AWS_ACCESS_KEY_ID="$$S3_ACCESS_KEY" -e AWS_SECRET_ACCESS_KEY="$$S3_SECRET_KEY" \
	  -e TF_VAR_s3_user="$$S3_ACCESS_KEY" -e TF_VAR_s3_password="$$S3_SECRET_KEY" \
	  -e TF_VAR_pg_user="$$POSTGRES_USER" -e TF_VAR_pg_password="$$POSTGRES_PASSWORD" \
	  $(TF_IMAGE) $(ARGS)

Q ?= h
VOICE ?= elevenlabs
video: ## Видео Manim + озвучка: make video SCENE=modules/…/x_video.py [Q=l|m|h] [VOICE=piper] → x.mp4
	$(COMPOSE) --profile media run --rm -e VOICE=$(VOICE) media "scripts/media/render.sh $(SCENE) $(Q)"

W ?= 1100
page-check: ## Проверка HTML-страницы в Chrome: make page-check PAGE=modules/…/visuals/x.html [W=390] [THEME=dark]
	$(COMPOSE) --profile media run --rm page-check $(PAGE) $(W) $(THEME); \
	  rc=$$?; $(COMPOSE) --profile media rm -sf chrome >/dev/null 2>&1; exit $$rc

check: ## Smoke-тест инфраструктуры (S3, Postgres, Iceberg-каталог, DuckDB)
	$(EXEC) python scripts/check_stack.py

data: ## Скачать датасет FreshRetailNet-50K в data/raw
	$(EXEC) python datasets/download_freshretail.py

ste: ## Стиль уроков по ASD-STE100: make ste [P=modules/00_just_enough/theory] [V=-v]
	$(EXEC) python scripts/ste_check.py $(V) $(P)

CI_STEPS ?= lint test dbt
ci: ## CI локально в чистом контейнере uv, без стека (модуль 12): make ci [CI_STEPS="lint"]
	docker run --rm -u $$(id -u):$$(id -g) -v $(CURDIR):/workspace -w /workspace -e HOME=/tmp \
	  -e UV_CACHE_DIR=/workspace/data/.uv-cache -e UV_PROJECT_ENVIRONMENT=/workspace/data/.ci-venv \
	  -e HF_HOME=/workspace/data/.hf_cache -e STATE_DIR=/workspace/data/ci_state \
	  $(UV_IMAGE) sh -c 'for s in $(CI_STEPS); do echo "== $$s"; scripts/ci/$$s.sh || exit 1; done'

precommit: ## pre-commit в контейнере (модуль 12): изменённые файлы; все — make precommit ARGS="--all-files"
	$(COMPOSE) exec -T -e PRE_COMMIT_HOME=/workspace/data/.pre-commit workspace pre-commit run $(ARGS)

hooks: ## Поставить git-хук pre-commit (модуль 12; нужен .git в корне курса)
	@test -d .git || { echo "нет .git в корне курса: хук ставится после выноса курса в свой репозиторий"; exit 1; }
	cp scripts/git-hooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
	@echo "хук установлен: .git/hooks/pre-commit → make precommit"

lint: ## Линтеры: ruff, sqlfmt --check, yamllint
	$(EXEC) sh -c 'ruff check . && ruff format --check . && sqlfmt --check . && yamllint -s infra'

fmt: ## Автоформатирование Python и SQL
	$(EXEC) sh -c 'ruff check --fix . && ruff format . && sqlfmt .'

test: ## pytest
	$(EXEC) pytest -q

obsidian: ## Поставить плагины Obsidian (версии — в scripts/obsidian_plugins.sh)
	docker run --rm -u $$(id -u):$$(id -g) -v $(CURDIR):/w -w /w $(CURL_IMAGE) \
	  sh scripts/obsidian_plugins.sh

clean: ## ОПАСНО: остановить всё и удалить тома с данными (Postgres, S3)
	@read -p "Удалить все тома с данными? [y/N] " a && [ "$$a" = y ]
	$(COMPOSE) --profile '*' down -v
