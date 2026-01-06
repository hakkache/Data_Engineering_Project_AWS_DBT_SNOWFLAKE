{{ config(
    materialized='table',
    unique_key='location_key',
    tags=['silver', 'dimension', 'location']
) }}

WITH source AS (
    SELECT * FROM {{ ref('bronze_OLIST_GEOLOCATION') }}
),

deduplicated AS (
    SELECT
        geolocation_zip_code_prefix,
        geolocation_lat,
        geolocation_lng,
        geolocation_city,
        geolocation_state,
        ROW_NUMBER() OVER (
            PARTITION BY geolocation_zip_code_prefix 
            ORDER BY created_at DESC
        ) AS rn
    FROM source
),

transformed AS (
    SELECT
        {{ generate_surrogate_key(['geolocation_zip_code_prefix']) }} AS location_key,
        {{ clean_string('geolocation_zip_code_prefix') }} AS zip_code_prefix,
        geolocation_lat AS latitude,
        geolocation_lng AS longitude,
        {{ clean_string('geolocation_city') }} AS city,
        {{ clean_string('geolocation_state') }} AS state,
        CURRENT_TIMESTAMP() AS updated_at
    FROM deduplicated
    WHERE rn = 1
)

SELECT * FROM transformed