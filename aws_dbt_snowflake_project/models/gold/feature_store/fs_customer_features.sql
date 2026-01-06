{{ config(
    materialized='table',
    tags=['gold', 'feature_store', 'customer']
) }}

-- Customer features updated daily for real-time ML predictions
SELECT
    customer_id,
    customer_state,
    customer_order_count,
    customer_lifetime_value,
    customer_avg_order_value,
    customer_tenure_days,
    CASE 
        WHEN customer_order_count = 1 THEN 'NEW'
        WHEN customer_order_count BETWEEN 2 AND 5 THEN 'REGULAR'
        ELSE 'LOYAL'
    END AS customer_segment,
    CURRENT_TIMESTAMP() AS feature_timestamp
FROM {{ ref('gold_obt_orders') }}
WHERE order_id = (
    SELECT MAX(order_id) 
    FROM {{ ref('gold_obt_orders') }} sub
    WHERE sub.customer_id = gold_obt_orders.customer_id
)