{{ config(materialized='incremental') }}

SELECT * FROM {{ source('staging', 'olist_geolocation') }} src

{% if is_incremental() %}
    WHERE src.created_at > (SELECT MAX(tgt.created_at) FROM {{ this }} tgt)
{% endif %}