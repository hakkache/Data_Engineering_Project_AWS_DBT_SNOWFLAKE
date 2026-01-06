{{ config(
    materialized='table',
    unique_key='product_key',
    tags=['silver', 'dimension', 'products']
) }}

WITH products AS (
    SELECT * FROM {{ ref('bronze_OLIST_PRODUCTS') }}
),

translations AS (
    SELECT * FROM {{ ref('bronze_PRODUCT_CATEGORY_NAME_TRANSLATION') }}
),

transformed AS (
    SELECT
        {{ generate_surrogate_key(['p.product_id']) }} AS product_key,
        p.product_id,
        {{ coalesce_default('p.product_category_name', 'UNKNOWN_CATEGORY') }} AS product_category_name,
        {{ coalesce_default('t.product_category_name_english', 'UNKNOWN') }} AS product_category_english,
        COALESCE(p.product_name_lenght, 0) AS product_name_length,
        COALESCE(p.product_description_lenght, 0) AS product_description_length,
        COALESCE(p.product_photos_qty, 0) AS product_photos_qty,
        COALESCE(p.product_weight_g, 0) AS product_weight_g,
        COALESCE(p.product_length_cm, 0) AS product_length_cm,
        COALESCE(p.product_height_cm, 0) AS product_height_cm,
        COALESCE(p.product_width_cm, 0) AS product_width_cm,
        -- Calculate volume
        (COALESCE(p.product_length_cm, 0) * 
         COALESCE(p.product_height_cm, 0) * 
         COALESCE(p.product_width_cm, 0)) AS product_volume_cm3,
        p.created_at,
        CURRENT_TIMESTAMP() AS updated_at
    FROM products p
    LEFT JOIN translations t 
        ON p.product_category_name = t.product_category_name
)

SELECT * FROM transformed