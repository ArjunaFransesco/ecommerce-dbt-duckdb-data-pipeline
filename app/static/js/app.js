document.addEventListener('DOMContentLoaded', () => {
    const sqlEditor = document.getElementById('sql-editor');
    const btnExecute = document.getElementById('btn-execute-sql');
    const spinner = document.getElementById('query-spinner');
    const btnText = btnExecute.querySelector('.btn-text');
    const queryStats = document.getElementById('query-stats');
    const resultsTable = document.getElementById('results-table');
    const btnTriggerPipeline = document.getElementById('btn-trigger-pipeline');

    // Preset Queries
    const queries = {
        rfm: `SELECT 
    customer_loyalty_tier,
    COUNT(*) AS total_customers,
    ROUND(SUM(lifetime_net_spend), 2) AS total_revenue_contribution,
    ROUND(AVG(avg_order_value), 2) AS avg_tier_aov,
    ROUND(AVG(recency_days), 1) AS avg_recency_days
FROM marts.dim_customers
GROUP BY customer_loyalty_tier
ORDER BY total_revenue_contribution DESC;`,

        top_products: `SELECT 
    product_name,
    product_category,
    price_tier,
    unit_price,
    lifetime_units_sold,
    lifetime_net_revenue,
    margin_percentage
FROM marts.dim_products
ORDER BY lifetime_net_revenue DESC
LIMIT 10;`,

        monthly_sales: `SELECT 
    d.year_month,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.gross_merchandise_value), 2) AS gross_sales,
    ROUND(SUM(f.net_merchandise_revenue), 2) AS net_sales,
    ROUND(SUM(f.total_discount_amount), 2) AS total_discounts
FROM marts.fct_orders f
JOIN marts.dim_date d ON f.order_date_key = d.date_key
WHERE f.is_successful_order = TRUE
GROUP BY d.year_month
ORDER BY d.year_month ASC;`,

        device_share: `SELECT 
    device_type,
    payment_method,
    COUNT(DISTINCT order_id) AS order_count,
    ROUND(SUM(net_merchandise_revenue), 2) AS total_revenue,
    ROUND(AVG(net_merchandise_revenue), 2) AS avg_ticket_size
FROM marts.fct_orders
WHERE is_successful_order = TRUE
GROUP BY device_type, payment_method
ORDER BY total_revenue DESC;`,

        cohort: `SELECT 
    cohort_month,
    activity_month,
    total_cohort_initial_size,
    active_retained_customers,
    retention_rate_percentage,
    total_cohort_revenue,
    avg_revenue_per_active_user
FROM marts.fct_monthly_cohort_retention
ORDER BY cohort_month DESC, activity_month ASC
LIMIT 20;`
    };

    // SQL Preset Buttons
    document.querySelectorAll('.btn-sql-preset').forEach(btn => {
        btn.addEventListener('click', () => {
            const qKey = btn.getAttribute('data-query');
            if (queries[qKey]) {
                sqlEditor.value = queries[qKey];
                executeSQL();
            }
        });
    });

    async function executeSQL() {
        const sql = sqlEditor.value.trim();
        if (!sql) return;

        btnExecute.disabled = true;
        spinner.style.display = 'inline-block';
        btnText.textContent = 'Running Query...';
        queryStats.textContent = 'Executing analytical scan in DuckDB...';

        try {
            const res = await fetch('/api/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sql })
            });

            const data = await res.json();
            if (data.status === 'success') {
                queryStats.textContent = `Returned ${data.row_count} rows in ${data.execution_time_ms} ms (DuckDB Columnar OLAP)`;
                renderTable(data.columns, data.rows);
            } else {
                queryStats.textContent = `Error: ${data.message}`;
                renderError(data.message);
            }
        } catch (e) {
            console.error('SQL Query Error:', e);
            queryStats.textContent = 'Network or execution error.';
        } finally {
            btnExecute.disabled = false;
            spinner.style.display = 'none';
            btnText.textContent = 'Execute SQL Query';
        }
    }

    function renderTable(columns, rows) {
        if (!columns || columns.length === 0) {
            resultsTable.innerHTML = '<thead><tr><th>Result</th></tr></thead><tbody><tr><td>Empty dataset returned.</td></tr></tbody>';
            return;
        }

        let thHtml = '<tr>' + columns.map(c => `<th>${c}</th>`).join('') + '</tr>';
        let tbHtml = rows.map(row => {
            return '<tr>' + columns.map(c => {
                let val = row[c];
                if (typeof val === 'number') {
                    val = Number.isInteger(val) ? val.toLocaleString() : val.toFixed(2);
                }
                return `<td>${val !== null && val !== undefined ? val : '<span style="color:#64748b;">NULL</span>'}</td>`;
            }).join('') + '</tr>';
        }).join('');

        resultsTable.innerHTML = `<thead>${thHtml}</thead><tbody>${tbHtml}</tbody>`;
    }

    function renderError(msg) {
        resultsTable.innerHTML = `<thead><tr><th style="color:#ef4444;">SQL Syntax / Execution Error</th></tr></thead><tbody><tr><td style="color:#f87171; font-family:var(--font-mono);">${msg}</td></tr></tbody>`;
    }

    btnExecute.addEventListener('click', executeSQL);

    // Re-run pipeline button
    btnTriggerPipeline.addEventListener('click', async () => {
        btnTriggerPipeline.disabled = true;
        btnTriggerPipeline.innerHTML = '<span class="spinner" style="display:inline-block;"></span> Running Ingestion & dbt...';

        try {
            const res = await fetch('/api/run-pipeline', { method: 'POST' });
            const data = await res.json();
            if (data.status === 'success') {
                alert(`Pipeline refreshed successfully in ${data.data.total_runtime_seconds}s!`);
                window.location.reload();
            } else {
                alert(`Pipeline Error: ${data.message}`);
            }
        } catch (err) {
            alert('Failed to trigger pipeline.');
        } finally {
            btnTriggerPipeline.disabled = false;
            btnTriggerPipeline.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg> Re-run Full ELT Pipeline';
        }
    });

    // Execute initial query on load
    executeSQL();
});
