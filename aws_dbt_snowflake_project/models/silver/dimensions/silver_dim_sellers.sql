{{ config(
    materialized='table',
    unique_key='seller_key',
    tags=['silver', 'dimension', 'sellers']
) }}

WITH source AS (
    SELECT * FROM {{ ref('bronze_OLIST_SELLERS') }}
),

transformed AS (
    SELECT
        {{ generate_surrogate_key(['seller_id']) }} AS seller_key,
        seller_id,
        {{ clean_string('seller_zip_code_prefix') }} AS seller_zip_code_prefix,
        {{ clean_string('seller_city') }} AS seller_city,
        {{ clean_string('seller_state') }} AS seller_state,
        created_at,
        CURRENT_TIMESTAMP() AS updated_at
    FROM source
)

SELECT * FROM transformed