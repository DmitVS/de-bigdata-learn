#!/bin/sh
# Идемпотентная инициализация Lakekeeper: bootstrap сервера и создание warehouse.
# Запускается сервисом lakekeeper-init при каждом `make up`, повторный запуск безопасен.
set -eu

API=http://lakekeeper:8181/management/v1

info=$(curl -sf "$API/info")
if echo "$info" | grep -q '"bootstrapped":true'; then
  echo "lakekeeper: уже bootstrapped"
else
  curl -sf -X POST "$API/bootstrap" \
    -H 'Content-Type: application/json' \
    -d '{"accept-terms-of-use": true}'
  echo "lakekeeper: bootstrap выполнен"
fi

if curl -sf "$API/warehouse" | grep -q "\"name\":\"${ICEBERG_WAREHOUSE}\""; then
  echo "lakekeeper: warehouse '${ICEBERG_WAREHOUSE}' уже существует"
  exit 0
fi

curl -sf -X POST "$API/warehouse" \
  -H 'Content-Type: application/json' \
  -d @- <<EOF
{
  "warehouse-name": "${ICEBERG_WAREHOUSE}",
  "storage-profile": {
    "type": "s3",
    "bucket": "warehouse",
    "key-prefix": "${ICEBERG_WAREHOUSE}",
    "endpoint": "http://silo:9000",
    "sts-endpoint": "http://silo:9000",
    "region": "local-01",
    "path-style-access": true,
    "flavor": "s3-compat",
    "sts-enabled": true
  },
  "storage-credential": {
    "type": "s3",
    "credential-type": "access-key",
    "access-key-id": "${S3_ACCESS_KEY}",
    "secret-access-key": "${S3_SECRET_KEY}"
  }
}
EOF
echo
echo "lakekeeper: warehouse '${ICEBERG_WAREHOUSE}' создан"
