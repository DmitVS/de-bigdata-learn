"""Настройка OpenMetadata для курса (модуль 11, make om-token): токен бота и сервис openlineage.

Сбор метаданных (make om-ingest) и агент OpenLineage в Spark (make spark-lineage) ходят в
OpenMetadata от имени бота: JWT-токен в заголовке. Токен создаёт сервер при первом запуске;
скрипт входит под администратором (admin@open-metadata.org / admin — учебный стек), читает
токен бота и записывает его в .env. После этого команды берут его из окружения.

Ещё скрипт создаёт сервис пайплайнов openlineage: события OpenLineage OpenMetadata привязывает
к нему и сам его не создаёт (в логе сервера: «Pipeline service 'openlineage' not found»).

Запуск (на хосте): make om-token
"""

import base64
import os
import re
from pathlib import Path

import requests

OM = os.environ.get("OM_URL", "http://openmetadata:8585/api/v1")
ENV_FILE = Path("/workspace/.env")


def main() -> None:
    password = base64.b64encode(b"admin").decode()
    login = requests.post(
        f"{OM}/users/login",
        json={"email": "admin@open-metadata.org", "password": password},
        timeout=30,
    )
    login.raise_for_status()
    headers = {"Authorization": f"Bearer {login.json()['accessToken']}"}

    bot = requests.get(f"{OM}/bots/name/ingestion-bot", headers=headers, timeout=30)
    bot.raise_for_status()
    user_id = bot.json()["botUser"]["id"]
    auth = requests.get(f"{OM}/users/auth-mechanism/{user_id}", headers=headers, timeout=30)
    auth.raise_for_status()
    token = auth.json()["config"]["JWTToken"]

    text = ENV_FILE.read_text()
    line = f"OM_INGESTION_TOKEN={token}"
    if re.search(r"^OM_INGESTION_TOKEN=.*$", text, flags=re.M):
        text = re.sub(r"^OM_INGESTION_TOKEN=.*$", line, text, flags=re.M)
    else:
        text = text.rstrip("\n") + "\n" + line + "\n"
    ENV_FILE.write_text(text)
    print(f"OM_INGESTION_TOKEN записан в .env ({len(token)} символов)")

    service = requests.put(
        f"{OM}/services/pipelineServices",
        headers=headers,
        json={
            "name": "openlineage",
            "serviceType": "OpenLineage",
            "connection": {"config": {"type": "OpenLineage"}},
        },
        timeout=30,
    )
    service.raise_for_status()
    print("сервис пайплайнов openlineage есть")


if __name__ == "__main__":
    main()
