{{ config(
    materialized='table',
    tags=['gold', 'fact', 'aggregate']
) }}

WITH orders AS (
    SELECT * FROM {{ ref('silver_fact_orders') }}
),

order_items AS (
    SELECT * FROM {{ ref('silver_fact_order_items') }}
),

payments AS (
    SELECT * FROM {{ ref('silver_fact_payments') }}
),

reviews AS (
    SELECT * FROM {{ ref('silver_fact_reviews') }}
),

order_aggregates AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.order_status,
        o.order_purchase_timestamp,
        o.order_date_key,
        o.actual_delivery_days,
        o.is_late_delivery,
        
        -- Order item metrics
        COUNT(DISTINCT oi.product_id) AS total_unique_products,
        COUNT(oi.order_item_id) AS total_items,
        SUM(oi.price) AS total_product_value,
        SUM(oi.freight_value) AS total_freight_value,
        SUM(oi.total_item_value) AS total_order_value,
        
        -- Payment metrics
        SUM(p.payment_value) AS total_payment_value,
        MAX(p.payment_installments) AS max_installments,
        LISTAGG(DISTINCT p.payment_type, ', ') AS payment_types_used,
        
        -- Review metrics
        MAX(r.review_score) AS review_score,
        MAX(r.review_sentiment) AS review_sentiment,
        MAX(r.has_comment) AS has_review_comment,
        
        CURRENT_TIMESTAMP() AS dw_created_at
    FROM orders o
    LEFT JOIN order_items oi ON o.order_id = oi.order_id
    LEFT JOIN payments p ON o.order_id = p.order_id
    LEFT JOIN reviews r ON o.order_id = r.order_id
    GROUP BY 1,2,3,4,5,6,7
)

SELECT * FROM order_aggregates