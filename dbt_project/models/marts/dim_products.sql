-- Marts Dimension: dim_products
-- Kimball Product Dimension enriched with lifetime sales velocity and margin analysis

WITH products AS (
    SELECT * FROM staging.stg_products
),

product_sales AS (
    SELECT
        product_id,
        COUNT(DISTINCT order_id) AS total_orders_featured,
        SUM(quantity) AS lifetime_units_sold,
        SUM(net_item_revenue) AS lifetime_net_revenue,
        SUM(total_item_discount) AS lifetime_discount_amount
    FROM staging.stg_order_items
    GROUP BY product_id
),

joined AS (
    SELECT
        p.product_id,
        p.product_name,
        p.product_category,
        p.unit_price,
        p.cost_price,
        p.unit_gross_margin,
        p.margin_percentage,
        p.is_active,
        COALESCE(ps.total_orders_featured, 0) AS total_orders_featured,
        COALESCE(ps.lifetime_units_sold, 0) AS lifetime_units_sold,
        ROUND(COALESCE(ps.lifetime_net_revenue, 0), 2) AS lifetime_net_revenue,
        ROUND(COALESCE(ps.lifetime_discount_amount, 0), 2) AS lifetime_discount_amount,
        CASE
            WHEN p.unit_price >= 250 THEN 'Premium / Luxury'
            WHEN p.unit_price >= 100 THEN 'Mid-to-High'
            WHEN p.unit_price >= 50  THEN 'Core Mass Market'
            ELSE 'Entry Level / Budget'
        END AS price_tier
    FROM products p
    LEFT JOIN product_sales ps ON p.product_id = ps.product_id
)

SELECT * FROM joined;
