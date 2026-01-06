{{ config(
    materialized='table',
    unique_key='customer_key',
    tags=['silver', 'dimension', 'customers']
) }}

WITH source AS (
    SELECT * FROM {{ ref('bronze_OLIST_CUSTOMERS') }}
),

transformed AS (
    SELECT
        {{ generate_surrogate_key(['customer_id']) }} AS customer_key,
        customer_id,
        customer_unique_id,
        {{ clean_string('customer_zip_code_prefix') }} AS customer_zip_code_prefix,
        {{ clean_string('customer_city') }} AS customer_city,
        {{ clean_string('customer_state') }} AS customer_state,
        created_at,
        CURRENT_TIMESTAMP() AS updated_at
    FROM source
)

SELECT * FROM transformed