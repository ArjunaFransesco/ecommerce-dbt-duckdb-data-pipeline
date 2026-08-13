-- Staging Model: stg_products
-- Standardizes product hierarchy, computes unit margin

WITH source AS (
    SELECT * FROM raw_staging.raw_products
),

cleaned AS (
    SELECT
        CAST(product_id AS BIGINT) AS product_id,
        TRIM(product_name) AS product_name,
        TRIM(category) AS product_category,
        ROUND(CAST(unit_price AS DOUBLE), 2) AS unit_price,
        ROUND(CAST(cost_price AS DOUBLE), 2) AS cost_price,
        ROUND(CAST(unit_price AS DOUBLE) - CAST(cost_price AS DOUBLE), 2) AS unit_gross_margin,
        ROUND(((CAST(unit_price AS DOUBLE) - CAST(cost_price AS DOUBLE)) / (CAST(unit_price AS DOUBLE) + 1e-6)) * 100, 2) AS margin_percentage,
        CAST(is_active AS BOOLEAN) AS is_active
    FROM source
)

SELECT * FROM cleaned;
