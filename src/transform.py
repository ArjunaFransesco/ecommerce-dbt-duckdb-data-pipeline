"""
DuckDB Transformation Engine & dbt-Style DAG Orchestrator
Executes Bronze -> Silver (Staging & Intermediate) -> Gold (Dimensional Marts) layers.
"""

import os
import sys
import duckdb
import pandas as pd
from typing import Dict, List, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


class DuckDBLakehouseEngine:
    """
    Embedded analytical OLAP engine managing raw ingestion, dbt SQL models, and star-schema marts.
    """
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or ":memory:"
        self.con = duckdb.connect(self.db_path)
        self.models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dbt_models")
        
    def load_raw_tables(self, raw_data: Dict[str, pd.DataFrame]):
        """Registers raw pandas dataframes into DuckDB as Bronze source tables."""
        for name, df in raw_data.items():
            table_name = f"raw_{name}"
            self.con.register(table_name, df)
            self.con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM {table_name}")
            print(f"[+] Loaded Bronze source table: {table_name} ({len(df):,} rows)")
            
    def execute_model_file(self, rel_path: str, view_or_table: str = "TABLE") -> str:
        """Reads SQL file from dbt_models and executes as a named view/table in DuckDB."""
        full_path = os.path.join(self.models_dir, rel_path)
        table_name = os.path.splitext(os.path.basename(rel_path))[0]
        
        with open(full_path, "r", encoding="utf-8") as f:
            sql_query = f.read()
            
        create_stmt = f"CREATE OR REPLACE {view_or_table} {table_name} AS \n{sql_query}"
        self.con.execute(create_stmt)
        count = self.con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"[+] Executed dbt Model: {table_name:<30} | {count:>7,} rows")
        return table_name

    def run_all_transformations(self):
        """Executes full dbt transformation DAG in topological dependency order."""
        print("\n--- [Phase 1] Staging Models (Silver - Cleaned & Normalized) ---")
        self.execute_model_file("staging/stg_customers.sql", "VIEW")
        self.execute_model_file("staging/stg_products.sql", "VIEW")
        self.execute_model_file("staging/stg_orders.sql", "VIEW")
        self.execute_model_file("staging/stg_order_items.sql", "VIEW")
        
        print("\n--- [Phase 2] Intermediate Business Logic Models (Silver - Joined) ---")
        self.execute_model_file("intermediate/int_order_items_enriched.sql", "TABLE")
        self.execute_model_file("intermediate/int_customer_metrics.sql", "TABLE")
        
        print("\n--- [Phase 3] Gold Dimensional Star-Schema & Analytical Marts ---")
        self.execute_model_file("marts/dim_customers.sql", "TABLE")
        self.execute_model_file("marts/dim_products.sql", "TABLE")
        self.execute_model_file("marts/dim_date.sql", "TABLE")
        self.execute_model_file("marts/fct_orders.sql", "TABLE")
        self.execute_model_file("marts/fct_customer_retention.sql", "TABLE")
        
    def query_to_df(self, sql_query: str) -> pd.DataFrame:
        """Executes arbitrary SQL query and returns Pandas DataFrame."""
        return self.con.execute(sql_query).fetchdf()

    def export_gold_marts_to_parquet(self, output_dir: str):
        """Exports Gold mart tables to parquet/csv files for downstream consumption."""
        os.makedirs(output_dir, exist_ok=True)
        marts = ["dim_customers", "dim_products", "dim_date", "fct_orders", "fct_customer_retention"]
        
        for m in marts:
            pq_path = os.path.join(output_dir, f"{m}.parquet")
            csv_path = os.path.join(output_dir, f"{m}.csv")
            self.con.execute(f"COPY {m} TO '{pq_path}' (FORMAT PARQUET)")
            self.con.execute(f"COPY {m} TO '{csv_path}' (HEADER, DELIMITER ',')")
        print(f"[+] Gold Marts successfully exported to {output_dir}")
