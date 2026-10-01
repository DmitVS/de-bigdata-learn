{#
  Публикация готовой модели в Iceberg (урок 02, шаг 5). Вызывается post-hook'ом с
  transaction: False — одна транзакция DuckDB может писать только в одну базу.
  DuckDB не умеет CREATE OR REPLACE для Iceberg, поэтому DROP + CREATE: между ними таблицы нет.
#}
{% macro publish_to_iceberg(namespace) %}
    {% if target.name == 'lake' %}
    CREATE SCHEMA IF NOT EXISTS lh.{{ namespace }};
    DROP TABLE IF EXISTS lh.{{ namespace }}.{{ this.identifier }};
    CREATE TABLE lh.{{ namespace }}.{{ this.identifier }} AS SELECT * FROM {{ this }};
    {% endif %}
{% endmacro %}
