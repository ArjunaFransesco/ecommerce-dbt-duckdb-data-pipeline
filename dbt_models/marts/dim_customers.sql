-- Marts: Dimension Customers (Star-Schema Conformed Dimension with RFM Value Tiers)
SELECT
    customer_id,
    full_name,
    email,
    city,
    country,
    signup_date,
    device_preference,
    total_orders_placed,
    total_successful_orders,
    first_order_at,
    latest_order_at,
    lifetime_net_revenue,
    lifetime_gross_profit,
    lifetime_items_purchased,
    average_order_value,
    CASE
        WHEN lifetime_net_revenue >= 1000.0 AND total_successful_orders >= 5 THEN 'VIP Champion'
        WHEN lifetime_net_revenue >= 500.0 THEN 'Loyal High Value'
        WHEN total_successful_orders >= 2 THEN 'Regular Customer'
        WHEN total_successful_orders = 1 THEN 'One-Time Buyer'
        ELSE 'Inactive / Lead'
    END AS customer_segment_tier
FROM int_customer_metrics;
