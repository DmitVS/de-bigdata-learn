"""Событие OpenLineage из своего Python-кода (модуль 11, урок 03).

У Spark есть агент, который сам собирает входы и выходы. У скрипта на Python (выгрузка, dlt,
ручная правка) агента нет — событие собирают сами клиентом openlineage-python. Скрипт
отправляет пару START → COMPLETE для «задачи» publish_city_report: она читает витрину
mart_city_oos_daily и пишет отчёт Evidence.

Транспорт выбирается аргументом:
    python emit_lineage.py console   # напечатать события (по умолчанию)
    python emit_lineage.py om        # отправить в OpenMetadata (нужен OM_INGESTION_TOKEN)
"""

import logging
import os
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

from openlineage.client import OpenLineageClient
from openlineage.client.event_v2 import InputDataset, Job, OutputDataset, Run, RunEvent, RunState
from openlineage.client.facet_v2 import schema_dataset, symlinks_dataset
from openlineage.client.transport.console import ConsoleConfig, ConsoleTransport
from openlineage.client.transport.http import ApiKeyTokenProvider, HttpConfig, HttpTransport

PRODUCER = "https://github.com/DmitVS/DE_BigData_Learn/modules/11_governance/demo/emit_lineage.py"


def om_token() -> str:
    """Токен бота: из окружения или из .env (make om-token пишет его после старта workspace)."""
    if os.environ.get("OM_INGESTION_TOKEN"):
        return os.environ["OM_INGESTION_TOKEN"]
    for line in Path("/workspace/.env").read_text().splitlines():
        if line.startswith("OM_INGESTION_TOKEN="):
            return line.split("=", 1)[1]
    raise SystemExit("нет OM_INGESTION_TOKEN: выполни make om-token")


def client(kind: str) -> OpenLineageClient:
    if kind == "om":
        config = HttpConfig(
            url="http://openmetadata:8585/api/v1/openlineage/",
            endpoint="lineage",
            auth=ApiKeyTokenProvider({"apiKey": om_token()}),
        )
        return OpenLineageClient(transport=HttpTransport(config))
    return OpenLineageClient(transport=ConsoleTransport(ConsoleConfig()))


def table(name: str) -> dict:
    """Facet symlinks: имя таблицы в каталоге — по нему OpenMetadata находит узел графа."""
    return {
        "symlinks": symlinks_dataset.SymlinksDatasetFacet(
            identifiers=[
                symlinks_dataset.Identifier(namespace="trino://trino:8080", name=name, type="TABLE")
            ]
        )
    }


def main() -> None:
    # ConsoleTransport печатает событие через logging на уровне INFO
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    ol = client(sys.argv[1] if len(sys.argv) > 1 else "console")
    run = Run(runId=str(uuid.uuid4()))
    job = Job(namespace="python_scripts", name="publish_city_report")
    inputs = [
        InputDataset(
            namespace="trino://trino:8080",
            name="iceberg.governance_demo.mart_city_oos_daily",
            facets=table("iceberg.governance_demo.mart_city_oos_daily")
            | {
                "schema": schema_dataset.SchemaDatasetFacet(
                    fields=[
                        schema_dataset.SchemaDatasetFacetFields(name="city_id", type="integer"),
                        schema_dataset.SchemaDatasetFacetFields(name="oos_hours", type="bigint"),
                    ]
                )
            },
        )
    ]
    outputs = [OutputDataset(namespace="file", name="/workspace/data/reports/city_report.html")]
    for state in (RunState.START, RunState.COMPLETE):
        ol.emit(
            RunEvent(
                eventType=state,
                # OpenMetadata принимает время только с суффиксом Z: «+00:00» даёт HTTP 400
                eventTime=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                run=run,
                job=job,
                producer=PRODUCER,
                inputs=inputs,
                outputs=outputs,
            )
        )


if __name__ == "__main__":
    main()
