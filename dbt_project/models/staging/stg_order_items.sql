-- Staging Model: stg_order_items
-- Calculates item-level gross and net revenue

WITH source AS (
    SELECT * FROM raw_staging.raw_order_items
),

cleaned AS (
    SELECT
        CAST(order_item_id AS BIGINT) AS order_item_id,
        CAST(order_id AS BIGINT) AS order_id,
        CAST(product_id AS BIGINT) AS product_id,
        CAST(quantity AS INT) AS quantity,
        ROUND(CAST(unit_price AS DOUBLE), 2) AS unit_price,
        ROUND(CAST(discount_percent AS DOUBLE), 4) AS discount_percent,
        ROUND(CAST(unit_price AS DOUBLE) * CAST(quantity AS INT), 2) AS gross_item_revenue,
        ROUND((CAST(unit_price AS DOUBLE) * (1.0 - CAST(discount_percent AS DOUBLE))) * CAST(quantity AS INT), 2) AS net_item_revenue,
        ROUND((CAST(unit_price AS DOUBLE) * CAST(discount_percent AS DOUBLE)) * CAST(quantity AS INT), 2) AS total_item_discount
    FROM source
)

SELECT * FROM cleaned;
