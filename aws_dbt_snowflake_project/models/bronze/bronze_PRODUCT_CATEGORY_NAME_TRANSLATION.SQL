{{config(materialized='incremental')}}

SELECT * FROM {{source('staging', 'product_category_name_translation')}}

{% if is_incremental() %}

    WHERE created_at > (SELECT MAX(created_at) FROM {{ this }})

{% endif %}