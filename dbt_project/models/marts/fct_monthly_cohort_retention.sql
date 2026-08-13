-- Marts Fact Table: fct_monthly_cohort_retention
-- Calculates monthly cohort retention rates, active customer counts, and net cohort revenues

WITH customer_cohort AS (
    SELECT
        customer_id,
        strftime(registration_date, '%Y-%m') AS cohort_month
    FROM staging.stg_customers
),

orders_by_month AS (
    SELECT
        customer_id,
        strftime(order_date, '%Y-%m') AS activity_month,
        COUNT(DISTINCT order_id) AS orders_count,
        SUM(net_merchandise_revenue) AS total_monthly_spend
    FROM marts.fct_orders
    WHERE is_successful_order = TRUE
    GROUP BY customer_id, strftime(order_date, '%Y-%m')
),

cohort_activity AS (
    SELECT
        c.cohort_month,
        o.activity_month,
        COUNT(DISTINCT c.customer_id) AS active_retained_customers,
        SUM(o.orders_count) AS total_cohort_orders,
        ROUND(SUM(o.total_monthly_spend), 2) AS total_cohort_revenue
    FROM customer_cohort c
    JOIN orders_by_month o ON c.customer_id = o.customer_id
    GROUP BY c.cohort_month, o.activity_month
),

cohort_size AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_id) AS total_cohort_initial_size
    FROM customer_cohort
    GROUP BY cohort_month
),

final AS (
    SELECT
        ca.cohort_month,
        ca.activity_month,
        cs.total_cohort_initial_size,
        ca.active_retained_customers,
        ROUND((CAST(ca.active_retained_customers AS DOUBLE) / cs.total_cohort_initial_size) * 100, 2) AS retention_rate_percentage,
        ca.total_cohort_orders,
        ca.total_cohort_revenue,
        ROUND(ca.total_cohort_revenue / ca.active_retained_customers, 2) AS avg_revenue_per_active_user
    FROM cohort_activity ca
    JOIN cohort_size cs ON ca.cohort_month = cs.cohort_month
    ORDER BY ca.cohort_month, ca.activity_month
)

SELECT * FROM final;
