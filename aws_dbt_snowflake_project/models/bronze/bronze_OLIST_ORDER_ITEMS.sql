{{config(materialized='incremental')}}

SELECT * FROM {{source('staging', 'olist_order_items')}}

{% if is_incremental() %}

    WHERE created_at > (SELECT MAX(created_at) FROM {{ this }})

{% endif %}