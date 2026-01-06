{{ config(
    materialized='incremental',
    unique_key='payment_key',
    incremental_strategy='merge',
    tags=['silver', 'fact', 'payments']
) }}

WITH source AS (
    SELECT * FROM {{ ref('bronze_OLIST_ORDER_PAYMENTS') }}
    {% if is_incremental() %}
    WHERE created_at > (SELECT MAX(updated_at) FROM {{ this }})
    {% endif %}
),

transformed AS (
    SELECT
        {{ generate_surrogate_key(['order_id', 'payment_sequential']) }} AS payment_key,
        order_id,
        payment_sequential,
        {{ clean_string('payment_type') }} AS payment_type,
        payment_installments,
        payment_value,
        created_at,
        CURRENT_TIMESTAMP() AS updated_at
    FROM source
)

SELECT * FROM transformed