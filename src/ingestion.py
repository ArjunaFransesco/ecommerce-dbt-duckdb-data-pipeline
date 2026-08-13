"""
Raw Ingestion Module for DuckDB Modern Data Stack Lakehouse.
Loads relational CSV files into raw_staging schema with column type validation.
"""

import os
import sys
import duckdb

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def ingest_raw_tables(
    db_path: str = "data/lakehouse/ecommerce_analytics.duckdb",
    raw_dir: str = "data/raw"
) -> duckdb.DuckDBPyConnection:
    """
    Ingests raw relational CSV files into DuckDB raw_staging schema.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    con = duckdb.connect(db_path)

    print(f"[+] Connected to DuckDB Lakehouse: {db_path}")
    con.execute("CREATE SCHEMA IF NOT EXISTS raw_staging;")

    tables = {
        "raw_customers": "customers.csv",
        "raw_products": "products.csv",
        "raw_orders": "orders.csv",
        "raw_order_items": "order_items.csv",
        "raw_payments": "payments.csv"
    }

    for table_name, filename in tables.items():
        file_path = os.path.join(raw_dir, filename).replace("\\", "/")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Raw source file not found: {file_path}")

        print(f"  [>] Ingesting {filename} -> raw_staging.{table_name}...")
        con.execute(f"""
            CREATE OR REPLACE TABLE raw_staging.{table_name} AS
            SELECT * FROM read_csv_auto('{file_path}', header=True);
        """)

        count = con.execute(f"SELECT COUNT(*) FROM raw_staging.{table_name}").fetchone()[0]
        print(f"      [✓] Ingested {count:,} rows into raw_staging.{table_name}")

    print("[+] Raw ingestion complete!\n")
    return con


if __name__ == "__main__":
    con = ingest_raw_tables()
    con.close()
