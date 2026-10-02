"""Общие фикстуры тестов демо модуля 07.

Тесты идут через Spark Connect на кластер слоя spark. Если кластер не поднят, тесты
пропускаются, а не падают: `make test` не должен требовать Spark.
"""

import socket

import pytest
from spark_demo.session import get_spark


def _connect_available(host: str = "spark-connect", port: int = 15002) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


@pytest.fixture(scope="session")
def spark():
    """Одна сессия на все тесты: подключение стоит ~1 с, а тестов много."""
    if not _connect_available():
        pytest.skip('нужен кластер Spark: make up PROFILES="spark"')
    return get_spark()
