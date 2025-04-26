{% macro test_assert_no_negative_values(model, column_name) %}
    SELECT
        {{ column_name }} AS invalid_value
    FROM {{ model }}
    WHERE {{ column_name }} < 0
{% endmacro %}
