-- Marts Dimension: dim_date
-- Standardized enterprise calendar dimension (2023 - 2026)

WITH date_spine AS (
    SELECT
        CAST('2023-01-01' AS DATE) + INTERVAL (d) DAY AS date_day
    FROM range(0, 1461) AS t(d)
),

transformed AS (
    SELECT
        date_day,
        CAST(strftime(date_day, '%Y%m%d') AS INT) AS date_key,
        EXTRACT(YEAR FROM date_day) AS year_actual,
        EXTRACT(QUARTER FROM date_day) AS quarter_actual,
        EXTRACT(MONTH FROM date_day) AS month_actual,
        strftime(date_day, '%B') AS month_name,
        strftime(date_day, '%b') AS month_short,
        EXTRACT(WEEK FROM date_day) AS week_of_year,
        EXTRACT(DAY FROM date_day) AS day_of_month,
        EXTRACT(DOW FROM date_day) AS day_of_week,
        strftime(date_day, '%A') AS day_name,
        CASE WHEN EXTRACT(DOW FROM date_day) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend,
        strftime(date_day, '%Y-%m') AS year_month
    FROM date_spine
)

SELECT * FROM transformed;
