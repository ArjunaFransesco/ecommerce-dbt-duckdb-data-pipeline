-- Marts: Dimension Products (Star-Schema Conformed Dimension with Catalog Metrics)
WITH product_sales AS (
    SELECT
        product_id,
        COUNT(DISTINCT order_id) AS total_orders_featured,
        SUM(quantity) AS total_units_sold,
        SUM(net_revenue) AS total_revenue_generated,
        SUM(gross_profit) AS total_profit_generated
    FROM int_order_items_enriched
    GROUP BY product_id
)
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.sub_category,
    p.cost_price,
    p.retail_price,
    p.unit_gross_margin,
    p.margin_percentage,
    p.is_active,
    COALESCE(ps.total_orders_featured, 0) AS total_orders_featured,
    COALESCE(ps.total_units_sold, 0) AS total_units_sold,
    COALESCE(ps.total_revenue_generated, 0.0) AS total_revenue_generated,
    COALESCE(ps.total_profit_generated, 0.0) AS total_profit_generated,
    CASE
        WHEN COALESCE(ps.total_units_sold, 0) >= 100 THEN 'Top Bestseller'
        WHEN COALESCE(ps.total_units_sold, 0) >= 30 THEN 'Steady Velocity'
        WHEN COALESCE(ps.total_units_sold, 0) > 0 THEN 'Low Volume'
        ELSE 'Zero Sales'
    END AS sales_velocity_tier
FROM stg_products p
LEFT JOIN product_sales ps ON p.product_id = ps.product_id;
