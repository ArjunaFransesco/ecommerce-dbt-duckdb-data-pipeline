-- Staging Model: stg_customers
-- Cleanses, trims, and standardizes raw customer dimensions

WITH source AS (
    SELECT * FROM raw_staging.raw_customers
),

cleaned AS (
    SELECT
        CAST(customer_id AS BIGINT) AS customer_id,
        TRIM(first_name) AS first_name,
        TRIM(last_name) AS last_name,
        CONCAT(TRIM(first_name), ' ', TRIM(last_name)) AS full_name,
        LOWER(TRIM(email)) AS email,
        TRIM(city) AS city,
        UPPER(TRIM(state)) AS state,
        TRIM(country) AS country,
        TRIM(segment) AS customer_segment,
        CAST(registration_date AS DATE) AS registration_date
    FROM source
)

SELECT * FROM cleaned;
