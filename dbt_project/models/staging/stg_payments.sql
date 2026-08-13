-- Staging Model: stg_payments
-- Validates payment transaction statuses and methods

WITH source AS (
    SELECT * FROM raw_staging.raw_payments
),

cleaned AS (
    SELECT
        CAST(payment_id AS BIGINT) AS payment_id,
        CAST(order_id AS BIGINT) AS order_id,
        TRIM(payment_method) AS payment_method,
        LOWER(TRIM(payment_status)) AS payment_status,
        ROUND(CAST(amount AS DOUBLE), 2) AS payment_amount,
        CAST(payment_timestamp AS TIMESTAMP) AS payment_timestamp
    FROM source
)

SELECT * FROM cleaned;
