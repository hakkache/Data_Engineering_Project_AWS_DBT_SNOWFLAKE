{{ config(materialized='incremental') }}

SELECT * FROM {{ source('staging', 'product_category_name_translation') }} src

{% if is_incremental() %}
    WHERE src.created_at > (SELECT MAX(tgt.created_at) FROM {{ this }} tgt)
{% endif %}