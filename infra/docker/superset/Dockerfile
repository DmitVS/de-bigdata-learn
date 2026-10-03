# Superset 6.1 + драйверы источников. Официальный образ «lean»: драйверов баз в нём нет,
# их ставят поверх в виртуальное окружение /app/.venv (Python 3.10 образа).
#   psycopg2-binary    — метаданные Superset в Postgres (база superset)
#   clickhouse-connect — подключение clickhousedb://
#   trino[sqlalchemy]  — подключение trino://
FROM apache/superset:6.1.0

USER root
RUN uv pip install --python /app/.venv/bin/python --no-cache \
      psycopg2-binary==2.9.11 \
      clickhouse-connect==1.9.0 \
      "trino[sqlalchemy]==0.340.0"
USER superset
