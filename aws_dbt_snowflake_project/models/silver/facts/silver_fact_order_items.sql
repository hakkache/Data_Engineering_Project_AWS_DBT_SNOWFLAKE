{{ config(
    materialized='incremental',
    unique_key='order_item_key',
    incremental_strategy='merge',
    tags=['silver', 'fact', 'order_items']
) }}

WITH source AS (
    SELECT * FROM {{ ref('bronze_OLIST_ORDER_ITEMS') }}
    {% if is_incremental() %}
    WHERE created_at > (SELECT MAX(updated_at) FROM {{ this }})
    {% endif %}
),

transformed AS (
    SELECT
        {{ generate_surrogate_key(['order_id', 'order_item_id']) }} AS order_item_key,
        order_id,
        order_item_id,
        product_id,
        seller_id,
        shipping_limit_date,
        price,
        freight_value,
        price + freight_value AS total_item_value,
        created_at,
        CURRENT_TIMESTAMP() AS updated_at
    FROM source
)

SELECT * FROM transformed