{{ config(
    materialized='table',
    tags=['gold', 'obt', 'ml', 'data_science']
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

customers AS (
    SELECT * FROM {{ ref('silver_dim_customers') }}
),

products AS (
    SELECT * FROM {{ ref('silver_dim_products') }}
),

sellers AS (
    SELECT * FROM {{ ref('silver_dim_sellers') }}
),

date_dim AS (
    SELECT * FROM {{ ref('silver_dim_date') }}
),

-- Customer historical features
customer_history AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS customer_order_count,
        SUM(total_order_value) AS customer_lifetime_value,
        AVG(total_order_value) AS customer_avg_order_value,
        MIN(order_purchase_timestamp) AS customer_first_order_date,
        MAX(order_purchase_timestamp) AS customer_last_order_date,
        DATEDIFF(DAY, MIN(order_purchase_timestamp), MAX(order_purchase_timestamp)) AS customer_tenure_days
    FROM (
        SELECT 
            o.customer_id,
            o.order_id,
            o.order_purchase_timestamp,
            SUM(oi.total_item_value) AS total_order_value
        FROM orders o
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY 1,2,3
    )
    GROUP BY 1
),

-- Product popularity features
product_features AS (
    SELECT
        product_id,
        COUNT(DISTINCT order_id) AS product_order_count,
        AVG(price) AS product_avg_price,
        SUM(price) AS product_total_revenue
    FROM order_items
    GROUP BY 1
),

-- Seller performance features
seller_features AS (
    SELECT
        seller_id,
        COUNT(DISTINCT order_id) AS seller_order_count,
        AVG(price) AS seller_avg_item_price
    FROM order_items
    GROUP BY 1
),

order_summary AS (
    SELECT
        o.order_id,
        o.order_key,
        
        -- ========================================
        -- CUSTOMER FEATURES (Demographic & Behavioral)
        -- ========================================
        c.customer_id,
        c.customer_unique_id,
        c.customer_city,
        c.customer_state,
        c.customer_zip_code_prefix,
        
        -- Customer history features (ML)
        ch.customer_order_count,
        ch.customer_lifetime_value,
        ch.customer_avg_order_value,
        ch.customer_tenure_days,
        DATEDIFF(DAY, ch.customer_last_order_date, o.order_purchase_timestamp) AS days_since_last_order,
        
        -- Customer segmentation (ML)
        CASE 
            WHEN ch.customer_order_count = 1 THEN 'NEW'
            WHEN ch.customer_order_count BETWEEN 2 AND 5 THEN 'REGULAR'
            WHEN ch.customer_order_count > 5 THEN 'LOYAL'
        END AS customer_segment,
        
        -- ========================================
        -- ORDER FEATURES (Target & Context)
        -- ========================================
        o.order_status,
        o.order_purchase_timestamp,
        o.order_approved_at,
        o.order_delivered_carrier_date,
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date,
        o.actual_delivery_days,
        o.estimated_delivery_days,
        o.is_late_delivery,
        
        -- ========================================
        -- TEMPORAL FEATURES (Time-based)
        -- ========================================
        d.year AS order_year,
        d.quarter AS order_quarter,
        d.month AS order_month,
        d.month_name AS order_month_name,
        d.week_of_year AS order_week,
        d.day_of_month AS order_day,
        d.day_of_week AS order_day_of_week,
        d.day_name AS order_day_name,
        d.is_weekend AS order_on_weekend,
        EXTRACT(HOUR FROM o.order_purchase_timestamp) AS order_hour,
        
        -- Time-based categories (ML)
        CASE 
            WHEN EXTRACT(HOUR FROM o.order_purchase_timestamp) BETWEEN 6 AND 11 THEN 'MORNING'
            WHEN EXTRACT(HOUR FROM o.order_purchase_timestamp) BETWEEN 12 AND 17 THEN 'AFTERNOON'
            WHEN EXTRACT(HOUR FROM o.order_purchase_timestamp) BETWEEN 18 AND 21 THEN 'EVENING'
            ELSE 'NIGHT'
        END AS order_time_of_day,
        
        -- ========================================
        -- PRODUCT FEATURES
        -- ========================================
        p.product_id,
        p.product_category_name,
        p.product_category_english,
        p.product_weight_g,
        p.product_length_cm,
        p.product_height_cm,
        p.product_width_cm,
        p.product_volume_cm3,
        p.product_photos_qty,
        
        -- Product popularity (ML)
        pf.product_order_count,
        pf.product_avg_price,
        pf.product_total_revenue,
        
        -- ========================================
        -- SELLER FEATURES
        -- ========================================
        s.seller_id,
        s.seller_city,
        s.seller_state,
        sf.seller_order_count,
        sf.seller_avg_item_price,
        
        -- Geographic features (ML)
        CASE WHEN c.customer_state = s.seller_state THEN 1 ELSE 0 END AS is_same_state,
        CASE WHEN c.customer_city = s.seller_city THEN 1 ELSE 0 END AS is_same_city,
        
        -- ========================================
        -- ORDER AGGREGATES (Numerical Features)
        -- ========================================
        COUNT(DISTINCT oi.product_id) AS total_unique_products,
        COUNT(oi.order_item_id) AS total_items,
        SUM(oi.price) AS total_product_value,
        SUM(oi.freight_value) AS total_freight_value,
        SUM(oi.total_item_value) AS total_order_value,
        AVG(oi.price) AS avg_item_price,
        MIN(oi.price) AS min_item_price,
        MAX(oi.price) AS max_item_price,
        STDDEV(oi.price) AS stddev_item_price,
        
        -- ========================================
        -- PAYMENT FEATURES
        -- ========================================
        SUM(pay.payment_value) AS total_payment_value,
        MAX(pay.payment_installments) AS max_installments,
        AVG(pay.payment_installments) AS avg_installments,
        COUNT(DISTINCT pay.payment_type) AS payment_types_count,
        LISTAGG(DISTINCT pay.payment_type, ', ') WITHIN GROUP (ORDER BY pay.payment_type) AS payment_types,
        
        -- Payment method indicators (ML - One-hot encoding)
        MAX(CASE WHEN pay.payment_type = 'CREDIT_CARD' THEN 1 ELSE 0 END) AS payment_credit_card,
        MAX(CASE WHEN pay.payment_type = 'BOLETO' THEN 1 ELSE 0 END) AS payment_boleto,
        MAX(CASE WHEN pay.payment_type = 'VOUCHER' THEN 1 ELSE 0 END) AS payment_voucher,
        MAX(CASE WHEN pay.payment_type = 'DEBIT_CARD' THEN 1 ELSE 0 END) AS payment_debit_card,
        
        -- ========================================
        -- REVIEW FEATURES (Sentiment & Quality)
        -- ========================================
        MAX(r.review_score) AS review_score,
        MAX(r.review_sentiment) AS review_sentiment,
        MAX(r.has_comment) AS has_review_comment,
        
        -- Sentiment indicators (ML)
        CASE WHEN MAX(r.review_score) >= 4 THEN 1 ELSE 0 END AS is_positive_review,
        CASE WHEN MAX(r.review_score) <= 2 THEN 1 ELSE 0 END AS is_negative_review,
        
        -- ========================================
        -- DERIVED BUSINESS METRICS (Target Variables)
        -- ========================================
        
        -- Delivery performance (Classification target)
        CASE 
            WHEN o.order_status = 'delivered' AND o.is_late_delivery = FALSE THEN 'ON_TIME'
            WHEN o.order_status = 'delivered' AND o.is_late_delivery = TRUE THEN 'LATE'
            WHEN o.order_status = 'canceled' THEN 'CANCELED'
            ELSE 'OTHER'
        END AS delivery_performance,
        
        -- Binary delivery target (ML)
        CASE WHEN o.is_late_delivery = TRUE THEN 1 ELSE 0 END AS is_delayed,
        
        -- Order value segment (ML)
        CASE 
            WHEN SUM(oi.total_item_value) >= 500 THEN 'HIGH_VALUE'
            WHEN SUM(oi.total_item_value) >= 100 THEN 'MEDIUM_VALUE'
            ELSE 'LOW_VALUE'
        END AS order_value_segment,
        
        -- Cancellation indicator (ML target)
        CASE WHEN o.order_status = 'canceled' THEN 1 ELSE 0 END AS is_canceled,
        
        -- Satisfaction proxy (ML target)
        CASE WHEN MAX(r.review_score) >= 4 THEN 1 ELSE 0 END AS is_satisfied,
        
        -- ========================================
        -- RATIOS & CALCULATED FEATURES (ML)
        -- ========================================
        SUM(oi.freight_value) / NULLIF(SUM(oi.price), 0) AS freight_to_product_ratio,
        SUM(oi.total_item_value) / NULLIF(COUNT(oi.order_item_id), 0) AS avg_value_per_item,
        MAX(pay.payment_installments) * SUM(pay.payment_value) AS total_credit_extended,
        
        -- ========================================
        -- METADATA
        -- ========================================
        CURRENT_TIMESTAMP() AS dw_created_at,
        '{{ run_started_at }}' AS dbt_run_timestamp
        
    FROM orders o
    LEFT JOIN customers c ON o.customer_id = c.customer_id
    LEFT JOIN customer_history ch ON c.customer_id = ch.customer_id
    LEFT JOIN order_items oi ON o.order_id = oi.order_id
    LEFT JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN product_features pf ON p.product_id = pf.product_id
    LEFT JOIN sellers s ON oi.seller_id = s.seller_id
    LEFT JOIN seller_features sf ON s.seller_id = sf.seller_id
    LEFT JOIN payments pay ON o.order_id = pay.order_id
    LEFT JOIN reviews r ON o.order_id = r.order_id
    LEFT JOIN date_dim d ON o.order_date_key = d.date_key
    GROUP BY 
        o.order_id,
        o.order_key,
        c.customer_id,
        c.customer_unique_id,
        c.customer_city,
        c.customer_state,
        c.customer_zip_code_prefix,
        ch.customer_order_count,
        ch.customer_lifetime_value,
        ch.customer_avg_order_value,
        ch.customer_tenure_days,
        ch.customer_last_order_date,
        o.order_purchase_timestamp,
        o.order_status,
        o.order_approved_at,
        o.order_delivered_carrier_date,
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date,
        o.actual_delivery_days,
        o.estimated_delivery_days,
        o.is_late_delivery,
        d.year,
        d.quarter,
        d.month,
        d.month_name,
        d.week_of_year,
        d.day_of_month,
        d.day_of_week,
        d.day_name,
        d.is_weekend,
        p.product_id,
        p.product_category_name,
        p.product_category_english,
        p.product_weight_g,
        p.product_length_cm,
        p.product_height_cm,
        p.product_width_cm,
        p.product_volume_cm3,
        p.product_photos_qty,
        pf.product_order_count,
        pf.product_avg_price,
        pf.product_total_revenue,
        s.seller_id,
        s.seller_city,
        s.seller_state,
        sf.seller_order_count,
        sf.seller_avg_item_price,
        c.customer_state,
        c.customer_city
)

SELECT * FROM order_summary