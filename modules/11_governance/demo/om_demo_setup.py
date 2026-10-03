"""Подготовка учебного каталога (модуль 11): команды-владельцы и пайплайн Spark.

1. Команды. Сбор dbt берёт владельца из meta.owner модели, но только если такая команда или
   пользователь уже есть в OpenMetadata. Иначе в логе: «Unable to ingest owner from DBT since
   no user or team was found with name …».
2. Пайплайн задачи Spark в сервисе openlineage. OpenMetadata 2.0.3 пытается создать его сам по
   первому событию OpenLineage и падает (`null value in column "updatedat"`): ребро появляется,
   но без пайплайна. Имя пайплайна = <namespace задачи>-<имя приложения Spark>.

Повторный запуск ничего не дублирует. Запуск (в make shell, после make om-token):
    python modules/11_governance/demo/om_demo_setup.py
"""

from pathlib import Path

import requests

OM = "http://openmetadata:8585/api/v1"
TEAMS = {
    "data-platform": "Платформа данных: загрузка, Spark, lakehouse",
    "retail-ops": "Операционный блок сети: учётная система магазинов",
    "analytics": "Аналитика: витрины, метрики, дашборды",
}

PIPELINES = {
    "spark_lineage-store_sales_daily": "Задача Spark: файлы → raw_sales → store_sales_daily",
}


def token() -> str:
    for line in Path("/workspace/.env").read_text().splitlines():
        if line.startswith("OM_INGESTION_TOKEN="):
            return line.split("=", 1)[1]
    raise SystemExit("нет OM_INGESTION_TOKEN: выполни make om-token")


def main() -> None:
    headers = {"Authorization": f"Bearer {token()}"}
    for name, description in TEAMS.items():
        r = requests.put(
            f"{OM}/teams",
            headers=headers,
            json={"name": name, "teamType": "Group", "description": description},
            timeout=30,
        )
        r.raise_for_status()
        print(f"команда {name}: {r.status_code}")

    for name, description in PIPELINES.items():
        r = requests.put(
            f"{OM}/pipelines",
            headers=headers,
            json={"name": name, "service": "openlineage", "description": description},
            timeout=30,
        )
        r.raise_for_status()
        print(f"пайплайн openlineage.{name}: {r.status_code}")


if __name__ == "__main__":
    main()
