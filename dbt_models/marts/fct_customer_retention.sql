-- Marts: Fact Monthly Cohort Customer Retention
WITH cohort_items AS (
    SELECT
        c.customer_id,
        STRFTIME(c.signup_date, '%Y-%m') AS cohort_month,
        STRFTIME(o.date_key, '%Y-%m') AS order_month,
        (EXTRACT(YEAR FROM o.date_key) - EXTRACT(YEAR FROM c.signup_date)) * 12 +
        (EXTRACT(MONTH FROM o.date_key) - EXTRACT(MONTH FROM c.signup_date)) AS month_number,
        o.order_id,
        o.net_merchandise_amount
    FROM dim_customers c
    JOIN fct_orders o ON c.customer_id = o.customer_id
    WHERE o.is_successful_order = 1
),
cohort_sizes AS (
    SELECT
        STRFTIME(signup_date, '%Y-%m') AS cohort_month,
        COUNT(DISTINCT customer_id) AS total_cohort_customers
    FROM dim_customers
    GROUP BY 1
)
SELECT
    ci.cohort_month,
    cs.total_cohort_customers,
    ci.month_number,
    COUNT(DISTINCT ci.customer_id) AS active_retained_customers,
    ROUND(COUNT(DISTINCT ci.customer_id) * 100.0 / cs.total_cohort_customers, 2) AS retention_rate_percentage,
    SUM(ci.net_merchandise_amount) AS cohort_revenue_generated
FROM cohort_items ci
JOIN cohort_sizes cs ON ci.cohort_month = cs.cohort_month
GROUP BY ci.cohort_month, cs.total_cohort_customers, ci.month_number
ORDER BY ci.cohort_month, ci.month_number;
