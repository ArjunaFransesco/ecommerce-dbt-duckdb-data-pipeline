-- Intermediate Order Items Enriched: Joining items with products to calculate item margins and product metadata
SELECT
    oi.item_id,
    oi.order_id,
    oi.product_id,
    p.product_name,
    p.category,
    p.sub_category,
    oi.quantity,
    oi.unit_price,
    oi.discount_amount,
    oi.gross_revenue,
    oi.net_revenue,
    CAST(p.cost_price * oi.quantity AS DECIMAL(10, 2)) AS total_cost,
    CAST(oi.net_revenue - (p.cost_price * oi.quantity) AS DECIMAL(10, 2)) AS gross_profit
FROM stg_order_items oi
LEFT JOIN stg_products p ON oi.product_id = p.product_id;
