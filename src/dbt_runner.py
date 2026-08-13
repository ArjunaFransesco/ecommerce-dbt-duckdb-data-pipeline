"""
dbt Transformation Engine & Automated Data Quality Test Runner for DuckDB.
Executes Staging views, Marts Star-Schema tables, and runs Data Quality assertions.
"""

import os
import sys
import time
import duckdb
from typing import Dict, Any, List

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


class DBTPipelineRunner:
    def __init__(self, db_path: str = "data/lakehouse/ecommerce_analytics.duckdb", dbt_dir: str = "dbt_project"):
        self.db_path = db_path
        self.dbt_dir = dbt_dir

    def run_transformations(self) -> Dict[str, Any]:
        start_time = time.time()
        con = duckdb.connect(self.db_path)
        print("=================================================================")
        print("          dbt ELT TRANSFORMATION & DATA MART MATERIALIZATION     ")
        print("=================================================================")

        con.execute("CREATE SCHEMA IF NOT EXISTS staging;")
        con.execute("CREATE SCHEMA IF NOT EXISTS marts;")

        # Order of execution based on DAG dependencies
        models = [
            ("staging", "stg_customers", "models/staging/stg_customers.sql", "VIEW"),
            ("staging", "stg_products", "models/staging/stg_products.sql", "VIEW"),
            ("staging", "stg_orders", "models/staging/stg_orders.sql", "VIEW"),
            ("staging", "stg_order_items", "models/staging/stg_order_items.sql", "VIEW"),
            ("staging", "stg_payments", "models/staging/stg_payments.sql", "VIEW"),
            ("marts", "dim_date", "models/marts/dim_date.sql", "TABLE"),
            ("marts", "dim_products", "models/marts/dim_products.sql", "TABLE"),
            ("marts", "dim_customers", "models/marts/dim_customers.sql", "TABLE"),
            ("marts", "fct_orders", "models/marts/fct_orders.sql", "TABLE"),
            ("marts", "fct_monthly_cohort_retention", "models/marts/fct_monthly_cohort_retention.sql", "TABLE")
        ]

        materialization_summary = []

        for schema, name, rel_path, mat_type in models:
            sql_path = os.path.join(self.dbt_dir, rel_path)
            if not os.path.exists(sql_path):
                raise FileNotFoundError(f"Model SQL not found: {sql_path}")

            with open(sql_path, "r", encoding="utf-8") as f:
                sql = f.read()

            t0 = time.time()
            if mat_type == "VIEW":
                con.execute(f"CREATE OR REPLACE VIEW {schema}.{name} AS {sql}")
            else:
                con.execute(f"CREATE OR REPLACE TABLE {schema}.{name} AS {sql}")
            elapsed = time.time() - t0

            row_count = con.execute(f"SELECT COUNT(*) FROM {schema}.{name}").fetchone()[0]
            print(f"  [OK] {mat_type:<5} {schema}.{name:<28} | {row_count:>7,d} rows | {elapsed * 1000:>6.2f} ms")
            materialization_summary.append({
                "schema": schema,
                "model_name": name,
                "materialization": mat_type,
                "row_count": row_count,
                "execution_ms": round(elapsed * 1000, 2)
            })

        total_elapsed = time.time() - start_time
        print(f"\n[+] Successfully built {len(models)} dbt models in {total_elapsed:.2f} seconds.")
        con.close()

        return {
            "status": "success",
            "total_models": len(models),
            "total_elapsed_sec": round(total_elapsed, 3),
            "models": materialization_summary
        }

    def run_data_quality_tests(self) -> Dict[str, Any]:
        """
        Executes automated Data Quality Contracts (dbt test equivalent)
        """
        con = duckdb.connect(self.db_path)
        print("\n=================================================================")
        print("          dbt DATA QUALITY & SCHEMA INTEGRITY TEST SUITE         ")
        print("=================================================================")

        tests = [
            # 1. Unique Primary Key Tests
            ("unique_stg_customers_id", "SELECT COUNT(*) FROM (SELECT customer_id, COUNT(*) FROM staging.stg_customers GROUP BY customer_id HAVING COUNT(*) > 1)"),
            ("unique_stg_products_id", "SELECT COUNT(*) FROM (SELECT product_id, COUNT(*) FROM staging.stg_products GROUP BY product_id HAVING COUNT(*) > 1)"),
            ("unique_stg_orders_id", "SELECT COUNT(*) FROM (SELECT order_id, COUNT(*) FROM staging.stg_orders GROUP BY order_id HAVING COUNT(*) > 1)"),
            ("unique_dim_customers_id", "SELECT COUNT(*) FROM (SELECT customer_id, COUNT(*) FROM marts.dim_customers GROUP BY customer_id HAVING COUNT(*) > 1)"),
            ("unique_dim_products_id", "SELECT COUNT(*) FROM (SELECT product_id, COUNT(*) FROM marts.dim_products GROUP BY product_id HAVING COUNT(*) > 1)"),
            ("unique_fct_orders_id", "SELECT COUNT(*) FROM (SELECT order_id, COUNT(*) FROM marts.fct_orders GROUP BY order_id HAVING COUNT(*) > 1)"),

            # 2. Not Null Constraint Tests
            ("not_null_stg_customers_email", "SELECT COUNT(*) FROM staging.stg_customers WHERE email IS NULL"),
            ("not_null_stg_orders_date", "SELECT COUNT(*) FROM staging.stg_orders WHERE order_date IS NULL"),
            ("not_null_dim_customers_tier", "SELECT COUNT(*) FROM marts.dim_customers WHERE customer_loyalty_tier IS NULL"),
            ("not_null_fct_orders_revenue", "SELECT COUNT(*) FROM marts.fct_orders WHERE net_merchandise_revenue IS NULL"),

            # 3. Referential Relationship Integrity Tests
            ("relationships_fct_orders_to_dim_customers", "SELECT COUNT(*) FROM marts.fct_orders f LEFT JOIN marts.dim_customers d ON f.customer_id = d.customer_id WHERE d.customer_id IS NULL"),
            ("relationships_stg_order_items_to_stg_products", "SELECT COUNT(*) FROM staging.stg_order_items oi LEFT JOIN staging.stg_products p ON oi.product_id = p.product_id WHERE p.product_id IS NULL"),

            # 4. Accepted Values Tests
            ("accepted_values_order_status", "SELECT COUNT(*) FROM marts.fct_orders WHERE order_status NOT IN ('completed', 'returned', 'cancelled', 'processing')"),
            ("accepted_values_loyalty_tier", "SELECT COUNT(*) FROM marts.dim_customers WHERE customer_loyalty_tier NOT IN ('VIP Platinum', 'Gold Tier', 'Silver Tier', 'Bronze Tier', 'Prospect (No Orders)')"),

            # 5. Positive Boundary Checks
            ("positive_values_fct_orders_gross_revenue", "SELECT COUNT(*) FROM marts.fct_orders WHERE gross_merchandise_value < 0"),
            ("positive_values_dim_products_price", "SELECT COUNT(*) FROM marts.dim_products WHERE unit_price < 0")
        ]

        test_results = []
        passed_count = 0

        for test_name, query in tests:
            t0 = time.time()
            failures = con.execute(query).fetchone()[0]
            elapsed = time.time() - t0

            passed = (failures == 0)
            if passed:
                passed_count += 1
                status_str = "PASS"
                color = "green"
            else:
                status_str = f"FAIL ({failures} violations)"
                color = "red"

            print(f"  [{status_str:<4}] {test_name:<46} | {elapsed * 1000:>5.2f} ms")
            test_results.append({
                "test_name": test_name,
                "status": "PASS" if passed else "FAIL",
                "failures_count": failures,
                "execution_ms": round(elapsed * 1000, 2)
            })

        con.close()
        pass_rate = round((passed_count / len(tests)) * 100, 2)
        print(f"\n[+] Completed {len(tests)} Data Quality Tests: {passed_count}/{len(tests)} PASSED ({pass_rate}% Pass Rate)\n")

        return {
            "total_tests": len(tests),
            "passed_tests": passed_count,
            "failed_tests": len(tests) - passed_count,
            "pass_rate_percentage": pass_rate,
            "test_details": test_results
        }


if __name__ == "__main__":
    runner = DBTPipelineRunner()
    mat_summary = runner.run_transformations()
    test_summary = runner.run_data_quality_tests()
