-- Выполняется один раз при первой инициализации тома postgres-data.
-- lakekeeper   — метаданные Iceberg REST-каталога
-- retail_oltp  — учебная «учётная система» сети (справочники магазинов/товаров/промо),
-- источник для ingestion (модуль 04) и CDC через Debezium (модуль 08)
CREATE DATABASE lakekeeper;
CREATE DATABASE retail_oltp;
