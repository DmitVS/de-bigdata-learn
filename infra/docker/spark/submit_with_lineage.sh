#!/bin/sh
# spark-submit в локальном режиме с агентом OpenLineage (модуль 11, сервис spark-lineage).
# События запуска уходят двумя путями (составной транспорт):
#   om   — HTTP в OpenMetadata: POST http://openmetadata:8585/api/v1/openlineage/lineage
#          (Java-клиент: адрес без пути, путь — целиком в endpoint, иначе ошибка «both uri and endpoint»),
#          токен бота — OM_INGESTION_TOKEN;
#   file — построчно JSON в data/openlineage/events.jsonl, чтобы прочитать событие глазами.
# Имя пространства задач (namespace) = имя сервиса пайплайнов в OpenMetadata.
set -e
mkdir -p /workspace/data/openlineage
exec /opt/spark/bin/spark-submit \
  --master "local[2]" \
  --conf spark.driver.memory=2g \
  --conf spark.extraListeners=io.openlineage.spark.agent.OpenLineageSparkListener \
  --conf spark.openlineage.namespace=spark_lineage \
  --conf spark.openlineage.transport.type=composite \
  --conf spark.openlineage.transport.continueOnFailure=true \
  --conf spark.openlineage.transport.transports.om.type=http \
  --conf spark.openlineage.transport.transports.om.url=http://openmetadata:8585 \
  --conf spark.openlineage.transport.transports.om.endpoint=/api/v1/openlineage/lineage \
  --conf spark.openlineage.transport.transports.om.auth.type=api_key \
  --conf spark.openlineage.transport.transports.om.auth.apiKey="${OM_INGESTION_TOKEN}" \
  --conf spark.openlineage.transport.transports.file.type=file \
  --conf spark.openlineage.transport.transports.file.location=/workspace/data/openlineage/events.jsonl \
  "$@"
