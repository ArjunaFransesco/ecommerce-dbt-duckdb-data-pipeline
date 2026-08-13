-- Intermediate Customer Metrics: Aggregating order history, lifetime value, and recency per customer
WITH customer_orders AS (
    SELECT
        o.customer_id,
        COUNT(DISTINCT o.order_id) AS total_orders_placed,
        SUM(o.is_successful_order) AS total_successful_orders,
        MIN(o.ordered_at) AS first_order_at,
        MAX(o.ordered_at) AS latest_order_at,
        SUM(CASE WHEN o.is_successful_order = 1 THEN o.shipping_cost ELSE 0 END) AS total_shipping_paid
    FROM stg_orders o
    GROUP BY o.customer_id
),
customer_revenues AS (
    SELECT
        o.customer_id,
        SUM(CASE WHEN o.is_successful_order = 1 THEN itm.net_revenue ELSE 0 END) AS lifetime_net_revenue,
        SUM(CASE WHEN o.is_successful_order = 1 THEN itm.gross_profit ELSE 0 END) AS lifetime_gross_profit,
        SUM(CASE WHEN o.is_successful_order = 1 THEN itm.quantity ELSE 0 END) AS lifetime_items_purchased
    FROM stg_orders o
    JOIN int_order_items_enriched itm ON o.order_id = itm.order_id
    GROUP BY o.customer_id
)
SELECT
    c.customer_id,
    c.full_name,
    c.email,
    c.city,
    c.country,
    c.signup_at,
    c.signup_date,
    c.device_preference,
    COALESCE(co.total_orders_placed, 0) AS total_orders_placed,
    COALESCE(co.total_successful_orders, 0) AS total_successful_orders,
    co.first_order_at,
    co.latest_order_at,
    COALESCE(cr.lifetime_net_revenue, 0.0) AS lifetime_net_revenue,
    COALESCE(cr.lifetime_gross_profit, 0.0) AS lifetime_gross_profit,
    COALESCE(cr.lifetime_items_purchased, 0) AS lifetime_items_purchased,
    CASE 
        WHEN COALESCE(co.total_successful_orders, 0) = 0 THEN 0.0
        ELSE ROUND(COALESCE(cr.lifetime_net_revenue, 0.0) / co.total_successful_orders, 2)
    END AS average_order_value
FROM stg_customers c
LEFT JOIN customer_orders co ON c.customer_id = co.customer_id
LEFT JOIN customer_revenues cr ON c.customer_id = cr.customer_id;
