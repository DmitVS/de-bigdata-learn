"""Настройки Superset учебного стека (модуль 10).

Метаданные (пользователи, подключения, датасеты, чарты, дашборды) хранятся в базе superset
общего Postgres, поэтому переживают пересоздание контейнера. Секреты — из окружения (.env).
"""

import os

SECRET_KEY = os.environ["SUPERSET_SECRET_KEY"]

SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg2://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}"
    "@postgres:5432/superset"
)

# Кэш результатов запросов чартов: 10 минут в памяти процесса. Redis в учебном стеке не нужен.
CACHE_CONFIG = {"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 600}
DATA_CACHE_CONFIG = CACHE_CONFIG

# Jinja в SQL Lab и виртуальных датасетах: {{ filter_values('city_id') }} и т.п.
FEATURE_FLAGS = {"ENABLE_TEMPLATE_PROCESSING": True}

# Загрузка CSV и примеры не нужны: данные приходят из витрин
SUPERSET_LOAD_EXAMPLES = False
