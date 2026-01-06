{% macro generate_date_spine(start_date, end_date) %}
WITH date_spine AS (
    SELECT 
        DATEADD(DAY, ROW_NUMBER() OVER (ORDER BY SEQ4()) - 1, '{{ start_date }}'::DATE) AS date_day
    FROM TABLE(GENERATOR(ROWCOUNT => DATEDIFF(DAY, '{{ start_date }}'::DATE, '{{ end_date }}'::DATE) + 1))
)
SELECT * FROM date_spine
{% endmacro %}