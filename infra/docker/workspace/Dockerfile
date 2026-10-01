# Рабочий контейнер: все Python-инструменты курса (dbt, dlt, DuckDB, Polars, PyIceberg, Jupyter, pre-commit).
# На хосте ничего, кроме Docker, не ставится. Репозиторий монтируется в /workspace,
# виртуальное окружение живёт в /opt/venv (вне монтирования, чтобы том его не перекрывал).
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ARG UID=1000
ARG GID=1000

RUN apt-get update \
    && apt-get install -y --no-install-recommends git make curl postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# DuckDB CLI — для интерактивной работы с SQL (Python-пакет duckdb ставится через uv)
ARG DUCKDB_VERSION=1.5.5
RUN curl -fsSL -o /tmp/duckdb.gz \
      "https://github.com/duckdb/duckdb/releases/download/v${DUCKDB_VERSION}/duckdb_cli-linux-amd64.gz" \
    && gunzip -c /tmp/duckdb.gz > /usr/local/bin/duckdb \
    && chmod +x /usr/local/bin/duckdb \
    && rm /tmp/duckdb.gz

RUN groupadd -g ${GID} dev && useradd -m -u ${UID} -g ${GID} -s /bin/bash dev \
    && mkdir -p /opt/venv && chown dev:dev /opt/venv

USER dev
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PATH=/opt/venv/bin:$PATH

WORKDIR /workspace
COPY --chown=dev:dev pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --all-groups
