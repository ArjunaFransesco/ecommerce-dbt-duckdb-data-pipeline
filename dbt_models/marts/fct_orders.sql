-- Marts: Fact Orders (Core Star-Schema Transactional Fact Table)
WITH order_item_summary AS (
    SELECT
        order_id,
        COUNT(DISTINCT item_id) AS distinct_items_count,
        SUM(quantity) AS total_quantity,
        SUM(gross_revenue) AS gross_order_amount,
        SUM(discount_amount) AS total_discount_amount,
        SUM(net_revenue) AS net_merchandise_amount,
        SUM(total_cost) AS total_order_cost,
        SUM(gross_profit) AS total_gross_profit
    FROM int_order_items_enriched
    GROUP BY order_id
)
SELECT
    o.order_id,
    o.customer_id,
    o.order_date AS date_key,
    o.order_date,
    o.ordered_at,
    o.order_status,
    o.is_successful_order,
    o.is_cancelled,
    o.is_returned,
    o.payment_method,
    o.shipping_cost,
    COALESCE(ois.distinct_items_count, 0) AS distinct_items_count,
    COALESCE(ois.total_quantity, 0) AS total_quantity,
    COALESCE(ois.gross_order_amount, 0.0) AS gross_order_amount,
    COALESCE(ois.total_discount_amount, 0.0) AS total_discount_amount,
    COALESCE(ois.net_merchandise_amount, 0.0) AS net_merchandise_amount,
    COALESCE(ois.total_order_cost, 0.0) AS total_order_cost,
    COALESCE(ois.total_gross_profit, 0.0) AS total_gross_profit,
    CAST(COALESCE(ois.net_merchandise_amount, 0.0) + o.shipping_cost AS DECIMAL(10, 2)) AS total_paid_amount
FROM stg_orders o
LEFT JOIN order_item_summary ois ON o.order_id = ois.order_id;
