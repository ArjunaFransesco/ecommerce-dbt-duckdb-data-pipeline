-- Staging Model: stg_orders
-- Normalizes order records and standardizes status codes

WITH source AS (
    SELECT * FROM raw_staging.raw_orders
),

cleaned AS (
    SELECT
        CAST(order_id AS BIGINT) AS order_id,
        CAST(customer_id AS BIGINT) AS customer_id,
        LOWER(TRIM(order_status)) AS order_status,
        CAST(order_timestamp AS TIMESTAMP) AS order_timestamp,
        CAST(order_timestamp AS DATE) AS order_date,
        TRIM(device_type) AS device_type,
        ROUND(CAST(shipping_cost AS DOUBLE), 2) AS shipping_cost,
        CASE
            WHEN LOWER(TRIM(order_status)) = 'completed' THEN TRUE
            ELSE FALSE
        END AS is_successful_order
    FROM source
)

SELECT * FROM cleaned;
