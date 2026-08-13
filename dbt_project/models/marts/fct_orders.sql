-- Marts Fact Table: fct_orders
-- Grain: One row per order, aggregated across line items and linked to payments and dimensions

WITH orders AS (
    SELECT * FROM staging.stg_orders
),

order_items_agg AS (
    SELECT
        order_id,
        COUNT(order_item_id) AS total_line_items_count,
        SUM(quantity) AS total_items_quantity,
        SUM(gross_item_revenue) AS gross_order_revenue,
        SUM(net_item_revenue) AS net_merchandise_revenue,
        SUM(total_item_discount) AS total_discount_amount,
        AVG(discount_percent) AS avg_item_discount_rate
    FROM staging.stg_order_items
    GROUP BY order_id
),

payments_agg AS (
    SELECT
        order_id,
        payment_method,
        payment_status,
        payment_amount,
        payment_timestamp
    FROM staging.stg_payments
),

joined AS (
    SELECT
        o.order_id,
        o.customer_id,
        CAST(strftime(o.order_date, '%Y%m%d') AS INT) AS order_date_key,
        o.order_date,
        o.order_timestamp,
        o.order_status,
        o.is_successful_order,
        o.device_type,
        o.shipping_cost,
        COALESCE(oi.total_line_items_count, 0) AS total_line_items_count,
        COALESCE(oi.total_items_quantity, 0) AS total_items_quantity,
        ROUND(COALESCE(oi.gross_order_revenue, 0), 2) AS gross_merchandise_value,
        ROUND(COALESCE(oi.total_discount_amount, 0), 2) AS total_discount_amount,
        ROUND(COALESCE(oi.net_merchandise_revenue, 0), 2) AS net_merchandise_revenue,
        ROUND(COALESCE(oi.net_merchandise_revenue, 0) + o.shipping_cost, 2) AS total_order_amount_billed,
        p.payment_method,
        p.payment_status,
        p.payment_amount,
        p.payment_timestamp
    FROM orders o
    LEFT JOIN order_items_agg oi ON o.order_id = oi.order_id
    LEFT JOIN payments_agg p ON o.order_id = p.order_id
)

SELECT * FROM joined;
