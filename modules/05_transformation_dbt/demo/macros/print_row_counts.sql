{# Операция: dbt run-operation print_row_counts. run_query выполняет SQL во время компиляции. #}
{% macro print_row_counts(schema='main') %}
    {% set tables = run_query(
      "select table_name from information_schema.tables where table_schema = '" ~ schema ~ "' order by 1"
  ) %}
    {% for row in tables.rows %}
        {% set n = run_query("select count(*) from " ~ schema ~ "." ~ row[0]).columns[0].values()[0] %}
        {{ log(row[0] ~ ": " ~ n, info=true) }}
    {% endfor %}
{% endmacro %}
