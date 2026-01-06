{% macro calculate_clv(customer_id_col, order_value_col, source_table) %}
    SUM({{ order_value_col }}) OVER (
        PARTITION BY {{ customer_id_col }}
        ORDER BY order_purchase_timestamp
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS customer_lifetime_value
{% endmacro %}

-- Categorize values into segments
{% macro value_segment(amount_column, high_threshold=500, medium_threshold=100) %}
    CASE 
        WHEN {{ amount_column }} >= {{ high_threshold }} THEN 'HIGH_VALUE'
        WHEN {{ amount_column }} >= {{ medium_threshold }} THEN 'MEDIUM_VALUE'
        ELSE 'LOW_VALUE'
    END
{% endmacro %}