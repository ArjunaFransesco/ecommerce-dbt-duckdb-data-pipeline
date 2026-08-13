"""
Automated Data Quality & Contract Assertion Testing Suite (dbt Test & Great Expectations Style)
"""

import sys
import pandas as pd
from typing import List, Dict, Any

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


class DataQualityTestSuite:
    """
    Executes automated schema assertions and referential integrity tests against DuckDB tables.
    """
    def __init__(self, engine):
        self.engine = engine
        self.results: List[Dict[str, Any]] = []

    def assert_unique(self, table: str, column: str):
        query = f"""
            SELECT {column}, COUNT(*) AS cnt
            FROM {table}
            GROUP BY {column}
            HAVING COUNT(*) > 1
        """
        violations = self.engine.con.execute(query).fetchall()
        passed = len(violations) == 0
        self.results.append({
            "test_type": "UNIQUE_KEY",
            "target": f"{table}.{column}",
            "passed": passed,
            "violations_count": len(violations),
            "severity": "CRITICAL"
        })

    def assert_not_null(self, table: str, column: str):
        query = f"SELECT COUNT(*) FROM {table} WHERE {column} IS NULL"
        null_count = self.engine.con.execute(query).fetchone()[0]
        passed = null_count == 0
        self.results.append({
            "test_type": "NOT_NULL",
            "target": f"{table}.{column}",
            "passed": passed,
            "violations_count": null_count,
            "severity": "CRITICAL"
        })

    def assert_accepted_values(self, table: str, column: str, allowed_values: List[str]):
        vals_str = ", ".join([f"'{v}'" for v in allowed_values])
        query = f"SELECT COUNT(*) FROM {table} WHERE {column} NOT IN ({vals_str})"
        invalid_count = self.engine.con.execute(query).fetchone()[0]
        passed = invalid_count == 0
        self.results.append({
            "test_type": "ACCEPTED_VALUES",
            "target": f"{table}.{column}",
            "passed": passed,
            "violations_count": invalid_count,
            "severity": "MEDIUM"
        })

    def assert_relationship(self, child_table: str, child_col: str, parent_table: str, parent_col: str):
        query = f"""
            SELECT COUNT(*)
            FROM {child_table} c
            LEFT JOIN {parent_table} p ON c.{child_col} = p.{parent_col}
            WHERE p.{parent_col} IS NULL
        """
        orphans = self.engine.con.execute(query).fetchone()[0]
        passed = orphans == 0
        self.results.append({
            "test_type": "FOREIGN_KEY_RELATIONSHIP",
            "target": f"{child_table}.{child_col} -> {parent_table}.{parent_col}",
            "passed": passed,
            "violations_count": orphans,
            "severity": "CRITICAL"
        })

    def assert_expression_positive(self, table: str, column: str):
        query = f"SELECT COUNT(*) FROM {table} WHERE {column} < 0"
        negatives = self.engine.con.execute(query).fetchone()[0]
        passed = negatives == 0
        self.results.append({
            "test_type": "NON_NEGATIVE_CONSTRAINT",
            "target": f"{table}.{column}",
            "passed": passed,
            "violations_count": negatives,
            "severity": "HIGH"
        })

    def run_full_suite(self) -> pd.DataFrame:
        """Executes full comprehensive data quality contract suite."""
        self.results = []
        
        # 1. Uniqueness checks on Primary Keys
        self.assert_unique("dim_customers", "customer_id")
        self.assert_unique("dim_products", "product_id")
        self.assert_unique("dim_date", "date_key")
        self.assert_unique("fct_orders", "order_id")
        
        # 2. Nullity checks on critical dimensions
        self.assert_not_null("dim_customers", "customer_id")
        self.assert_not_null("dim_customers", "email")
        self.assert_not_null("dim_products", "product_name")
        self.assert_not_null("fct_orders", "order_id")
        self.assert_not_null("fct_orders", "customer_id")
        self.assert_not_null("fct_orders", "net_merchandise_amount")
        
        # 3. Referential Integrity (Foreign Keys)
        self.assert_relationship("fct_orders", "customer_id", "dim_customers", "customer_id")
        self.assert_relationship("int_order_items_enriched", "product_id", "dim_products", "product_id")
        
        # 4. Accepted Values / Enums
        self.assert_accepted_values("dim_customers", "customer_segment_tier", [
            "VIP Champion", "Loyal High Value", "Regular Customer", "One-Time Buyer", "Inactive / Lead"
        ])
        self.assert_accepted_values("dim_products", "sales_velocity_tier", [
            "Top Bestseller", "Steady Velocity", "Low Volume", "Zero Sales"
        ])
        
        # 5. Non-negative checks
        self.assert_expression_positive("fct_orders", "net_merchandise_amount")
        self.assert_expression_positive("dim_products", "retail_price")
        
        df_results = pd.DataFrame(self.results)
        passed_cnt = df_results["passed"].sum()
        total_cnt = len(df_results)
        
        print("\n" + "=" * 70)
        print(f"       DATA QUALITY & CONTRACT TEST SUITE: {passed_cnt}/{total_cnt} PASSED       ")
        print("=" * 70)
        for _, row in df_results.iterrows():
            status = "[PASS]" if row["passed"] else "[FAIL]"
            print(f"  {status} {row['test_type']:<26} | {row['target']:<45} (Violations: {row['violations_count']})")
        print("=" * 70)
        
        return df_results
