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
.PHONY: help init lock uv build up down restart ps logs shell sql check data lint fmt test obsidian clean dagster dagster-shell rpk flink-sql

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
	$(COMPOSE) logs -f --tail=200 $(S)

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

check: ## Smoke-тест инфраструктуры (S3, Postgres, Iceberg-каталог, DuckDB)
	$(EXEC) python scripts/check_stack.py

data: ## Скачать датасет FreshRetailNet-50K в data/raw
	$(EXEC) python datasets/download_freshretail.py

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
