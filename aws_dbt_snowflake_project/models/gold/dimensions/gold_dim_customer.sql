{{ config(
    materialized='incremental',
    unique_key='customer_surrogate_key',
    incremental_strategy='merge',
    tags=['gold', 'dimension', 'scd2']
) }}

WITH current_customers AS (
    SELECT
        {{ generate_surrogate_key(['customer_id', 'customer_unique_id', 'customer_state']) }} AS customer_surrogate_key,
        customer_key,
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state,
        created_at AS effective_start_date,
        '9999-12-31'::DATE AS effective_end_date,
        TRUE AS is_current,
        CURRENT_TIMESTAMP() AS dw_created_at,
        CURRENT_TIMESTAMP() AS dw_updated_at
    FROM {{ ref('silver_dim_customers') }}
    
    {% if is_incremental() %}
    WHERE updated_at > (SELECT MAX(dw_updated_at) FROM {{ this }})
    {% endif %}
)

SELECT * FROM current_customers