{{ config(
    materialized='table',
    unique_key='date_key',
    tags=['silver', 'dimension', 'date']
) }}

WITH date_spine AS (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2016-01-01' as date)",
        end_date="cast('2025-12-31' as date)"
    ) }}
),

date_details AS (
    SELECT
        TO_CHAR(date_day, 'YYYYMMDD')::INTEGER AS date_key,
        date_day AS full_date,
        EXTRACT(YEAR FROM date_day) AS year,
        EXTRACT(QUARTER FROM date_day) AS quarter,
        EXTRACT(MONTH FROM date_day) AS month,
        TO_CHAR(date_day, 'Month') AS month_name,
        EXTRACT(WEEK FROM date_day) AS week_of_year,
        EXTRACT(DAY FROM date_day) AS day_of_month,
        EXTRACT(DOW FROM date_day) AS day_of_week,
        TO_CHAR(date_day, 'Day') AS day_name,
        EXTRACT(DOY FROM date_day) AS day_of_year,
        CASE WHEN EXTRACT(DOW FROM date_day) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend,
        DATE_TRUNC('month', date_day) AS first_day_of_month,
        LAST_DAY(date_day) AS last_day_of_month,
        CURRENT_TIMESTAMP() AS created_at
    FROM date_spine
)

SELECT * FROM date_details