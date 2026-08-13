"""
Flask Application & OLAP Analytics API for Modern E-Commerce Data Stack.
Provides interactive SQL workbench, data lineage explorer, and real-time executive BI.
"""

import json
import os
import sys
import time
import duckdb

# Add project root and src directory to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from flask import Flask, jsonify, render_template, request
from src.pipeline import run_full_pipeline

app = Flask(__name__)

DB_PATH = os.path.join(PROJECT_ROOT, "data", "lakehouse", "ecommerce_analytics.duckdb")
REPORTS_PATH = os.path.join(PROJECT_ROOT, "reports", "pipeline_execution_summary.json")


def get_pipeline_summary():
    if os.path.exists(REPORTS_PATH):
        with open(REPORTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@app.route("/")
def home():
    summary = get_pipeline_summary()
    return render_template("index.html", summary=summary)


@app.route("/api/overview", methods=["GET"])
def api_overview():
    summary = get_pipeline_summary()
    return jsonify({"status": "success", "data": summary})


@app.route("/api/query", methods=["POST"])
def api_query():
    """
    Executes analytical SQL query on DuckDB OLAP marts.
    """
    try:
        payload = request.get_json(force=True)
        sql = payload.get("sql", "").strip()

        if not sql:
            return jsonify({"status": "error", "message": "SQL query cannot be empty"}), 400

        # Disallow destructive queries for safety
        disallowed = ["DROP", "DELETE", "TRUNCATE", "ALTER", "UPDATE", "INSERT"]
        if any(keyword in sql.upper().split() for keyword in disallowed):
            return jsonify({"status": "error", "message": "Only read-only analytical SELECT queries are permitted in the BI workbench."}), 403

        con = duckdb.connect(DB_PATH, read_only=True)
        t0 = time.time()
        df_result = con.execute(sql).df()
        elapsed_ms = round((time.time() - t0) * 1000, 2)
        con.close()

        # Format dates/timestamps for JSON serialization
        for col in df_result.columns:
            if str(df_result[col].dtype).startswith("datetime") or str(df_result[col].dtype).startswith("date"):
                df_result[col] = df_result[col].astype(str)

        return jsonify({
            "status": "success",
            "execution_time_ms": elapsed_ms,
            "row_count": len(df_result),
            "columns": list(df_result.columns),
            "rows": df_result.head(100).to_dict(orient="records")
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/cohorts", methods=["GET"])
def api_cohorts():
    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        df_cohorts = con.execute("""
            SELECT
                cohort_month,
                activity_month,
                total_cohort_initial_size,
                active_retained_customers,
                retention_rate_percentage,
                total_cohort_revenue,
                avg_revenue_per_active_user
            FROM marts.fct_monthly_cohort_retention
            ORDER BY cohort_month, activity_month;
        """).df()
        con.close()

        return jsonify({
            "status": "success",
            "data": df_cohorts.to_dict(orient="records")
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/run-pipeline", methods=["POST"])
def api_run_pipeline():
    try:
        summary = run_full_pipeline(db_path=DB_PATH)
        return jsonify({"status": "success", "data": summary})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "active", "engine": "DuckDB Modern Data Stack Lakehouse v1.0"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5003))
    print(f"[*] Starting Modern Data Stack Lakehouse BI Dashboard on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
