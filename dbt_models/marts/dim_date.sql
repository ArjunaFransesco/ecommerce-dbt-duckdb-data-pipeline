-- Marts: Dimension Date (Star-Schema Conformed Temporal Dimension)
WITH date_series AS (
    SELECT UNNEST(GENERATE_SERIES(DATE '2023-01-01', DATE '2026-12-31', INTERVAL 1 DAY)) AS date_day
)
SELECT
    date_day AS date_key,
    EXTRACT(YEAR FROM date_day) AS calendar_year,
    EXTRACT(MONTH FROM date_day) AS calendar_month,
    EXTRACT(DAY FROM date_day) AS calendar_day,
    EXTRACT(QUARTER FROM date_day) AS calendar_quarter,
    EXTRACT(DOW FROM date_day) AS day_of_week,
    STRFTIME(date_day, '%A') AS day_name,
    STRFTIME(date_day, '%B') AS month_name,
    CASE WHEN EXTRACT(DOW FROM date_day) IN (0, 6) THEN 1 ELSE 0 END AS is_weekend
FROM date_series;
