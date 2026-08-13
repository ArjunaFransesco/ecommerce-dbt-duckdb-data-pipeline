"""
Master Orchestrator Pipeline for Modern E-Commerce Data Stack.
Executes end-to-end ELT lifecycle: Ingestion -> dbt Transformations -> Data Quality Contracts -> Analytical Reporting.
"""

import os
import sys
import json
import time
import duckdb

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from raw_generator import generate_ecommerce_raw_data
from ingestion import ingest_raw_tables
from dbt_runner import DBTPipelineRunner


def run_full_pipeline(
    db_path: str = "data/lakehouse/ecommerce_analytics.duckdb",
    raw_dir: str = "data/raw",
    reports_dir: str = "reports"
):
    start_time = time.time()
    os.makedirs(reports_dir, exist_ok=True)

    print("#################################################################")
    print("#       MODERN DATA STACK (MDS) END-TO-END PIPELINE RUNNER      #")
    print("#################################################################\n")

    # Step 1: Raw Data Generation (if not present)
    if not os.path.exists(os.path.join(raw_dir, "orders.csv")):
        generate_ecommerce_raw_data(output_dir=raw_dir)

    # Step 2: Raw Staging Ingestion into DuckDB
    ingest_raw_tables(db_path=db_path, raw_dir=raw_dir)

    # Step 3: dbt Materializations
    dbt_runner = DBTPipelineRunner(db_path=db_path)
    mat_results = dbt_runner.run_transformations()

    # Step 4: Data Quality & Schema Integrity Tests
    test_results = dbt_runner.run_data_quality_tests()

    # Step 5: Extract Analytical Executive KPIs from Star-Schema Marts
    print("=================================================================")
    print("             EXECUTIVE OLAP DATA MART KPI SUMMARY                ")
    print("=================================================================")
    con = duckdb.connect(db_path)

    kpis = con.execute("""
        SELECT
            COUNT(DISTINCT order_id) AS total_orders,
            COUNT(DISTINCT customer_id) AS total_unique_customers,
            ROUND(SUM(gross_merchandise_value), 2) AS total_gross_merchandise_value,
            ROUND(SUM(net_merchandise_revenue), 2) AS total_net_revenue,
            ROUND(SUM(total_discount_amount), 2) AS total_discounts_given,
            ROUND(AVG(net_merchandise_revenue), 2) AS average_order_value
        FROM marts.fct_orders
        WHERE is_successful_order = TRUE;
    """).df().to_dict(orient="records")[0]

    print(f"[*] Total Completed Orders:    {kpis['total_orders']:,}")
    print(f"[*] Unique Transacting Users:  {kpis['total_unique_customers']:,}")
    print(f"[*] Total Gross Revenue (GMV): ${kpis['total_gross_merchandise_value']:,.2f}")
    print(f"[*] Total Net Revenue:         ${kpis['total_net_revenue']:,.2f}")
    print(f"[*] Average Order Value (AOV): ${kpis['average_order_value']:,.2f}")

    # Top 5 Products by Revenue
    top_products = con.execute("""
        SELECT
            product_name,
            product_category,
            lifetime_units_sold,
            lifetime_net_revenue,
            margin_percentage
        FROM marts.dim_products
        ORDER BY lifetime_net_revenue DESC
        LIMIT 5;
    """).df().to_dict(orient="records")

    # Customer Loyalty Tier breakdown
    loyalty_tiers = con.execute("""
        SELECT
            customer_loyalty_tier,
            COUNT(*) AS customer_count,
            ROUND(SUM(lifetime_net_spend), 2) AS tier_revenue
        FROM marts.dim_customers
        GROUP BY customer_loyalty_tier
        ORDER BY tier_revenue DESC;
    """).df().to_dict(orient="records")

    con.close()

    total_pipeline_time = round(time.time() - start_time, 2)

    summary_payload = {
        "pipeline_name": "Modern E-Commerce ELT Lakehouse",
        "engine": "DuckDB OLAP + dbt SQL Transformations",
        "execution_status": "SUCCESS",
        "total_runtime_seconds": total_pipeline_time,
        "executive_kpis": kpis,
        "top_revenue_products": top_products,
        "loyalty_tier_breakdown": loyalty_tiers,
        "dbt_materializations": mat_results,
        "data_quality_report": test_results
    }

    report_path = os.path.join(reports_dir, "pipeline_execution_summary.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2)

    print(f"\n[+] Pipeline execution completed successfully in {total_pipeline_time}s!")
    print(f"[+] Saved execution metadata & test summary to: {report_path}")
    print("#################################################################\n")

    return summary_payload


if __name__ == "__main__":
    run_full_pipeline()
