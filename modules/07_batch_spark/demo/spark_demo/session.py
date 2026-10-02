"""Подключение к кластеру и отчёт по стадиям для уроков модуля 07.

    from spark_demo.session import get_spark, StageReport
    spark = get_spark()
    with StageReport("groupBy по магазинам"):
        df.groupBy("store_id").count().collect()

StageReport печатает стадии, завершившиеся внутри блока, с числом задач, входными строками,
объёмом shuffle и разбросом времени задач. Данные берутся из REST API Spark UI
(http://spark-connect:4040/api/v1) — то же, что видно на вкладке Stages.
"""

import json
import os
import time
import urllib.request

from pyspark.sql import SparkSession

CONNECT_URL = os.environ.get("SPARK_CONNECT_URL", "sc://spark-connect:15002")
UI_API = os.environ.get("SPARK_UI_API", "http://spark-connect:4040/api/v1")


def get_spark() -> SparkSession:
    """Сессия Spark Connect: план уходит на сервер spark-connect, считают executors на workers."""
    return SparkSession.builder.remote(CONNECT_URL).getOrCreate()


def _get(path: str):
    with urllib.request.urlopen(f"{UI_API}{path}") as resp:
        return json.load(resp)


def _app_id() -> str:
    return _get("/applications")[0]["id"]


def _kb(n: int) -> str:
    return f"{n / 1024:,.0f} КБ" if n < 100 * 1024 * 1024 else f"{n / 1048576:,.0f} МБ"


class StageReport:
    """Контекстный менеджер: какие стадии выполнились внутри блока и с какими метриками."""

    def __init__(self, label: str):
        self.label = label

    def __enter__(self):
        self.app = _app_id()
        stages = _get(f"/applications/{self.app}/stages")
        self.last = max((s["stageId"] for s in stages), default=-1)
        self.started = time.time()
        return self

    def __exit__(self, *exc):
        elapsed = time.time() - self.started
        time.sleep(0.5)  # UI получает события асинхронно
        stages = [
            s
            for s in _get(f"/applications/{self.app}/stages")
            if s["stageId"] > self.last and s["status"] == "COMPLETE"
        ]
        print(f"== {self.label}: {elapsed:.2f} с, стадий {len(stages)}")
        for s in sorted(stages, key=lambda s: s["stageId"]):
            summary = _get(
                f"/applications/{self.app}/stages/{s['stageId']}/{s['attemptId']}"
                "/taskSummary?quantiles=0.5,1.0"
            )
            median, slowest = summary["executorRunTime"]
            print(
                f"   стадия {s['stageId']}: задач {s['numTasks']}, "
                f"прочитано строк {s['inputRecords']:,}, "
                f"shuffle запись {_kb(s['shuffleWriteBytes'])} "
                f"({s['shuffleWriteRecords']:,} строк), "
                f"shuffle чтение {_kb(s['shuffleReadBytes'])}, "
                f"задача медиана/макс {median / 1000:.2f}/{slowest / 1000:.2f} с, "
                f"spill {_kb(s['diskBytesSpilled'])}"
            )
        return False
