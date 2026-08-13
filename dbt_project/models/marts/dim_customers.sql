-- Marts Dimension: dim_customers
-- Kimball Customer Dimension enriched with RFM metrics and customer lifetime tiers

WITH customers AS (
    SELECT * FROM staging.stg_customers
),

order_summary AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS total_lifetime_orders,
        COUNT(DISTINCT CASE WHEN is_successful_order THEN order_id END) AS completed_orders_count,
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS last_order_date,
        DATEDIFF('day', MAX(order_date), CAST('2025-01-01' AS DATE)) AS recency_days
    FROM staging.stg_orders
    GROUP BY customer_id
),

order_financials AS (
    SELECT
        o.customer_id,
        COALESCE(SUM(oi.gross_item_revenue), 0) AS total_gross_spend,
        COALESCE(SUM(oi.net_item_revenue), 0) AS total_net_spend,
        COALESCE(SUM(oi.total_item_discount), 0) AS total_discounts_received,
        COALESCE(AVG(oi.net_item_revenue), 0) AS avg_item_spend
    FROM staging.stg_orders o
    LEFT JOIN staging.stg_order_items oi ON o.order_id = oi.order_id
    WHERE o.is_successful_order = TRUE
    GROUP BY o.customer_id
),

joined AS (
    SELECT
        c.customer_id,
        c.full_name,
        c.email,
        c.city,
        c.state,
        c.country,
        c.customer_segment,
        c.registration_date,
        COALESCE(os.total_lifetime_orders, 0) AS total_lifetime_orders,
        COALESCE(os.completed_orders_count, 0) AS completed_orders_count,
        os.first_order_date,
        os.last_order_date,
        COALESCE(os.recency_days, 999) AS recency_days,
        ROUND(COALESCE(f.total_gross_spend, 0), 2) AS lifetime_gross_spend,
        ROUND(COALESCE(f.total_net_spend, 0), 2) AS lifetime_net_spend,
        ROUND(COALESCE(f.total_discounts_received, 0), 2) AS lifetime_discounts_received,
        CASE
            WHEN COALESCE(os.completed_orders_count, 0) > 0
                THEN ROUND(COALESCE(f.total_net_spend, 0) / os.completed_orders_count, 2)
            ELSE 0.0
        END AS avg_order_value,
        CASE
            WHEN COALESCE(f.total_net_spend, 0) >= 2000 THEN 'VIP Platinum'
            WHEN COALESCE(f.total_net_spend, 0) >= 1000 THEN 'Gold Tier'
            WHEN COALESCE(f.total_net_spend, 0) >= 350  THEN 'Silver Tier'
            WHEN COALESCE(f.total_net_spend, 0) > 0    THEN 'Bronze Tier'
            ELSE 'Prospect (No Orders)'
        END AS customer_loyalty_tier
    FROM customers c
    LEFT JOIN order_summary os ON c.customer_id = os.customer_id
    LEFT JOIN order_financials f ON c.customer_id = f.customer_id
)

SELECT * FROM joined;
