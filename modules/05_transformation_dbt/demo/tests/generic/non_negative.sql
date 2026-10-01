-- Свой generic-тест: параметры model и column_name dbt подставит из YAML
{% test non_negative(model, column_name) %}
    select {{ column_name }} from {{ model }} where {{ column_name }} < 0
{% endtest %}
