{{ config(
    materialized='incremental',
    unique_key='order_key',
    incremental_strategy='merge',
    tags=['silver', 'fact', 'orders']
) }}

WITH source AS (
    SELECT * FROM {{ ref('bronze_OLIST_ORDERS') }}
    {% if is_incremental() %}
    WHERE created_at > (SELECT MAX(updated_at) FROM {{ this }})
    {% endif %}
),

transformed AS (
    SELECT
        {{ generate_surrogate_key(['order_id']) }} AS order_key,
        order_id,
        customer_id,
        {{ coalesce_default('order_status', 'UNKNOWN') }} AS order_status,
        order_purchase_timestamp,
        order_approved_at,
        order_delivered_carrier_date,
        order_delivered_customer_date,
        order_estimated_delivery_date,
        -- Calculate delivery metrics
        DATEDIFF(DAY, order_purchase_timestamp, order_delivered_customer_date) AS actual_delivery_days,
        DATEDIFF(DAY, order_purchase_timestamp, order_estimated_delivery_date) AS estimated_delivery_days,
        CASE 
            WHEN order_delivered_customer_date > order_estimated_delivery_date THEN TRUE 
            ELSE FALSE 
        END AS is_late_delivery,
        TO_CHAR(order_purchase_timestamp, 'YYYYMMDD')::INTEGER AS order_date_key,
        created_at,
        CURRENT_TIMESTAMP() AS updated_at
    FROM source
)

SELECT * FROM transformed