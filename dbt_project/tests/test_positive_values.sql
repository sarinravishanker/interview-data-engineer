{% test positive_values(model, column) %}
WITH validation AS (
    SELECT
        {{ column }} AS value
    FROM {{ model }}
    WHERE {{ column }} <= 0
)
SELECT COUNT(*) AS invalid_count
FROM validation
{% endtest %}
