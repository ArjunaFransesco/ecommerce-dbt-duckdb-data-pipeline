-- Staging Products: Standardizing categories, margins, and active status
SELECT
    TRIM(product_id) AS product_id,
    TRIM(product_name) AS product_name,
    TRIM(category) AS category,
    TRIM(sub_category) AS sub_category,
    CAST(cost_price AS DECIMAL(10, 2)) AS cost_price,
    CAST(retail_price AS DECIMAL(10, 2)) AS retail_price,
    CAST(retail_price - cost_price AS DECIMAL(10, 2)) AS unit_gross_margin,
    ROUND((retail_price - cost_price) / (retail_price + 1e-5) * 100.0, 2) AS margin_percentage,
    CAST(is_active AS BOOLEAN) AS is_active
FROM raw_products;
