-- Staging Order Items: Item-level revenues and discount calculations
SELECT
    TRIM(item_id) AS item_id,
    TRIM(order_id) AS order_id,
    TRIM(product_id) AS product_id,
    CAST(quantity AS INTEGER) AS quantity,
    CAST(unit_price AS DECIMAL(10, 2)) AS unit_price,
    CAST(discount_amount AS DECIMAL(10, 2)) AS discount_amount,
    CAST((quantity * unit_price) AS DECIMAL(10, 2)) AS gross_revenue,
    CAST((quantity * unit_price) - discount_amount AS DECIMAL(10, 2)) AS net_revenue
FROM raw_order_items;
