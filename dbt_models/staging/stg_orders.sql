-- Staging Orders: Timestamps, status flags, and shipping costs
SELECT
    TRIM(order_id) AS order_id,
    TRIM(customer_id) AS customer_id,
    CAST(order_timestamp AS TIMESTAMP) AS ordered_at,
    CAST(order_timestamp AS DATE) AS order_date,
    TRIM(order_status) AS order_status,
    CASE 
        WHEN TRIM(order_status) IN ('Completed', 'Delivered', 'Shipped') THEN 1 
        ELSE 0 
    END AS is_successful_order,
    CASE 
        WHEN TRIM(order_status) = 'Cancelled' THEN 1 
        ELSE 0 
    END AS is_cancelled,
    CASE 
        WHEN TRIM(order_status) = 'Returned' THEN 1 
        ELSE 0 
    END AS is_returned,
    TRIM(payment_method) AS payment_method,
    CAST(shipping_cost AS DECIMAL(10, 2)) AS shipping_cost
FROM raw_orders;
