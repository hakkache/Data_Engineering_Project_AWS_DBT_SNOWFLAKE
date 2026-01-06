{{ config(
    materialized='incremental',
    unique_key='review_key',
    incremental_strategy='merge',
    tags=['silver', 'fact', 'reviews']
) }}

WITH source AS (
    SELECT * FROM {{ ref('bronze_OLIST_ORDER_REVIEWS') }}
    {% if is_incremental() %}
    WHERE created_at > (SELECT MAX(updated_at) FROM {{ this }})
    {% endif %}
),

transformed AS (
    SELECT
        {{ generate_surrogate_key(['review_id']) }} AS review_key,
        review_id,
        order_id,
        review_score,
        review_comment_title,
        review_comment_message,
        review_creation_date,
        review_answer_timestamp,
        -- Calculate review sentiment
        CASE 
            WHEN review_score >= 4 THEN 'POSITIVE'
            WHEN review_score = 3 THEN 'NEUTRAL'
            ELSE 'NEGATIVE'
        END AS review_sentiment,
        -- Check if has comment
        CASE 
            WHEN review_comment_message IS NOT NULL AND TRIM(review_comment_message) != '' 
            THEN TRUE ELSE FALSE 
        END AS has_comment,
        created_at,
        CURRENT_TIMESTAMP() AS updated_at
    FROM source
)

SELECT * FROM transformed