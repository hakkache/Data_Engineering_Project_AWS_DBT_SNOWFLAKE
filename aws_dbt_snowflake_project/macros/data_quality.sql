{% macro clean_string(column_name) %}
    TRIM(UPPER({{ column_name }}))
{% endmacro %}

-- Handle nulls with default
{% macro coalesce_default(column_name, default_value='UNKNOWN') %}
    COALESCE(NULLIF(TRIM({{ column_name }}), ''), '{{ default_value }}')
{% endmacro %}

-- Remove duplicates based on column
{% macro deduplicate(source_table, partition_by, order_by='created_at DESC') %}
    WITH ranked AS (
        SELECT *,
            ROW_NUMBER() OVER (
                PARTITION BY {{ partition_by }}
                ORDER BY {{ order_by }}
            ) AS rn
        FROM {{ source_table }}
    )
    SELECT * EXCEPT(rn)
    FROM ranked
    WHERE rn = 1
{% endmacro %}