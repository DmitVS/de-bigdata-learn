{# Макрос-функция: возвращает SQL-выражение, а не данные. Пороги — аргументы со значениями по умолчанию. #}
{% macro precipitation_bucket(column, light=1.0, heavy=10.0) %}
    case
        when {{ column }} is null
        then 'unknown'
        when {{ column }} < {{ light }}
        then 'dry'
        when {{ column }} < {{ heavy }}
        then 'light'
        else 'heavy'
    end
{% endmacro %}
