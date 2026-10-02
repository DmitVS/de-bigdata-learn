"""Ресурсы учебного проекта: внешние системы, которые ассеты получают параметром.

Ресурс отделяет «что делает ассет» от «куда он подключается»: в тестах его подменяют, а адреса и
ключи берутся из окружения контейнера (урок 02, шаг 4).
"""

import os

import duckdb
import s3fs
from dagster import ConfigurableResource, EnvVar


class S3Resource(ConfigurableResource):
    """S3-хранилище Silo. Ключи — из переменных окружения workspace."""

    endpoint_url: str = EnvVar("S3_ENDPOINT")
    access_key: str = EnvVar("AWS_ACCESS_KEY_ID")
    secret_key: str = EnvVar("AWS_SECRET_ACCESS_KEY")

    def filesystem(self) -> s3fs.S3FileSystem:
        # skip_instance_cache: fsspec по умолчанию переиспользует объект с теми же аргументами
        # вместе с кэшем списков файлов. В долгоживущем code-сервере сенсор тогда не увидит
        # перезаписанный файл (урок 03, шаг 4).
        return s3fs.S3FileSystem(
            endpoint_url=self.endpoint_url,
            key=self.access_key,
            secret=self.secret_key,
            skip_instance_cache=True,
        )


class DuckDBResource(ConfigurableResource):
    """Файл DuckDB учебного проекта. Писать в него может только один процесс одновременно."""

    path: str = "/workspace/data/demo_orchestration.duckdb"

    def connect(self, read_only: bool = False) -> duckdb.DuckDBPyConnection:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        return duckdb.connect(self.path, read_only=read_only)
