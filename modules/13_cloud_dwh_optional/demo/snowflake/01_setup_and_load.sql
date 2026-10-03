-- Snowflake (модуль 13): склад вычислений, база, загрузка файлов датасета.
-- ВНИМАНИЕ: файл проверен по документации Snowflake, а не на стеке курса — нужен аккаунт
-- (trial). Выполнять в Snowsight (Worksheets) под ролью ACCOUNTADMIN или SYSADMIN.
--
-- 1. Склад вычислений: самый маленький размер и автоостановка через 60 с простоя —
--    кредиты тратятся только пока склад работает.
CREATE WAREHOUSE IF NOT EXISTS de_wh
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;

CREATE DATABASE IF NOT EXISTS de_course;
CREATE SCHEMA IF NOT EXISTS de_course.raw;
USE SCHEMA de_course.raw;

-- 2. Внутренний stage — место для файлов внутри Snowflake. Parquet читается по схеме файла.
CREATE FILE FORMAT IF NOT EXISTS parquet_ff TYPE = PARQUET;
CREATE STAGE IF NOT EXISTS freshretail_stage FILE_FORMAT = parquet_ff;

-- 3. Файлы кладутся в stage из Snowsight (Data → Add data → Load files into a stage) или
--    командой PUT из Snowflake CLI / Python-коннектора (урок 02):
--    PUT file:///workspace/data/raw/freshretailnet_50k/data/*.parquet @freshretail_stage;
LIST @freshretail_stage;

-- 4. Таблица по схеме Parquet без ручного перечисления колонок.
CREATE OR REPLACE TABLE sales USING TEMPLATE (
    SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
    FROM TABLE(INFER_SCHEMA(LOCATION => '@freshretail_stage', FILE_FORMAT => 'parquet_ff'))
);

COPY INTO sales
FROM @freshretail_stage
FILE_FORMAT = (FORMAT_NAME = 'parquet_ff')
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

-- Ожидание: 4 850 000 строк (train + eval), 97 дней — как в lakehouse.
SELECT COUNT(*) AS rows, MIN("dt") AS dt_from, MAX("dt") AS dt_to FROM sales;
