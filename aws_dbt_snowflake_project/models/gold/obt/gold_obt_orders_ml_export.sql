{{ config(
    materialized='view',
    tags=['gold', 'obt', 'ml', 'export']
) }}

-- This view selects only numerical and encoded features for direct ML consumption
SELECT
    -- IDs
    order_id,
    
    -- ========== NUMERICAL FEATURES ==========
    customer_order_count,
    customer_lifetime_value,
    customer_avg_order_value,
    customer_tenure_days,
    days_since_last_order,
    
    actual_delivery_days,
    estimated_delivery_days,
    
    order_year,
    order_quarter,
    order_month,
    order_week,
    order_day,
    order_day_of_week,
    order_hour,
    order_on_weekend::INT AS order_on_weekend,
    
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm,
    product_volume_cm3,
    product_photos_qty,
    product_order_count,
    product_avg_price,
    
    seller_order_count,
    seller_avg_item_price,
    is_same_state,
    is_same_city,
    
    total_unique_products,
    total_items,
    total_product_value,
    total_freight_value,
    total_order_value,
    avg_item_price,
    min_item_price,
    max_item_price,
    stddev_item_price,
    
    max_installments,
    avg_installments,
    payment_types_count,
    payment_credit_card,
    payment_boleto,
    payment_voucher,
    payment_debit_card,
    
    review_score,
    is_positive_review,
    is_negative_review,
    
    freight_to_product_ratio,
    avg_value_per_item,
    total_credit_extended,
    
    -- ========== TARGET VARIABLES ==========
    is_delayed,
    is_canceled,
    is_satisfied,
    review_score AS target_review_score,
    actual_delivery_days AS target_delivery_days

FROM {{ ref('gold_obt_orders') }}
WHERE order_status = 'delivered'