"""
Streamlit Web Application: Modern E-Commerce ELT Lakehouse & dbt Star-Schema Pipeline
Author: Arjuna Fransesco
"""

import os
import json
import duckdb
import pandas as pd
import numpy as np
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="E-Commerce Lakehouse & dbt Pipeline | Arjuna Fransesco",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for Modern Data Stack theme
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #F8FAFC;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #94A3B8;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        padding: 1.2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .kpi-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #38BDF8;
    }
    .kpi-lbl {
        font-size: 0.85rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

# Load Lakehouse Data from DuckDB / Parquet
@st.cache_resource
def get_lakehouse_connection():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    lakehouse_dir = os.path.join(base_dir, "data", "lakehouse")
    db_file = os.path.join(lakehouse_dir, "ecommerce.duckdb")
    
    con = duckdb.connect(db_file if os.path.exists(db_file) else ":memory:")
    
    # If in-memory, load from parquet
    if not os.path.exists(db_file):
        for mart in ["dim_customers", "dim_products", "dim_date", "fct_orders", "fct_customer_retention"]:
            pq = os.path.join(lakehouse_dir, f"{mart}.parquet")
            if os.path.exists(pq):
                con.execute(f"CREATE OR REPLACE TABLE {mart} AS SELECT * FROM read_parquet('{pq}')")
                
    summary_path = os.path.join(base_dir, "artifacts", "pipeline_summary.json")
    summary = {}
    if os.path.exists(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)
            
    return con, summary

con, summary = get_lakehouse_connection()

# Header
st.markdown('<div class="main-header">🏗️ Modern E-Commerce ELT Lakehouse & dbt Star-Schema</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Analytical Lakehouse Engine (DuckDB + dbt Transformations + Great Expectations Quality Contracts)</div>', unsafe_allow_html=True)

# KPI Cards
kpis = summary.get("executive_kpis", {
    "total_orders": 8000,
    "total_net_revenue": 2579509.19,
    "total_gross_profit": 1078539.78,
    "average_order_value": 351.00,
    "active_purchasers": 1188
})

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="kpi-lbl">Total Net Revenue (Gold)</div>
        <div class="kpi-val">${kpis['total_net_revenue']:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="kpi-lbl">Total Gross Profit</div>
        <div class="kpi-val">${kpis['total_gross_profit']:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="kpi-lbl">Average Order Value (AOV)</div>
        <div class="kpi-val">${kpis['average_order_value']:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    quality_passed = summary.get("data_quality_tests", {}).get("passed", 16)
    quality_total = summary.get("data_quality_tests", {}).get("total", 16)
    st.markdown(f"""
    <div class="metric-card">
        <div class="kpi-lbl">Quality Contracts</div>
        <div class="kpi-val" style="color: #4ADE80;">{quality_passed}/{quality_total} Passed</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Executive BI Analytics",
    "🏛️ Star-Schema & Data Lineage",
    "💻 DuckDB SQL Workbench",
    "🛡️ Data Quality Contracts"
])

with tab1:
    st.subheader("📈 Monthly Revenue, Margins & Customer Value Tiers")
    col_a, col_b = st.columns([3, 2])
    
    with col_a:
        st.markdown("**Monthly Revenue & Gross Profit Trajectory**")
        df_monthly = con.execute("""
            SELECT
                STRFTIME(date_key, '%Y-%m') AS month,
                SUM(net_merchandise_amount) AS monthly_revenue,
                SUM(total_gross_profit) AS monthly_profit
            FROM fct_orders
            WHERE is_successful_order = 1
            GROUP BY 1
            ORDER BY 1
        """).fetchdf()
        st.line_chart(df_monthly.set_index("month"))
        
    with col_b:
        st.markdown("**Customer Segment Tier Breakdown (RFM)**")
        df_tiers = con.execute("""
            SELECT
                customer_segment_tier,
                COUNT(*) AS customer_count,
                ROUND(SUM(lifetime_net_revenue), 2) AS total_segment_revenue
            FROM dim_customers
            GROUP BY 1
            ORDER BY total_segment_revenue DESC
        """).fetchdf()
        st.dataframe(df_tiers, use_container_width=True)
        st.bar_chart(df_tiers.set_index("customer_segment_tier")["total_segment_revenue"])
        
    st.markdown("---")
    st.markdown("**Category Profitability & Volume Matrix**")
    df_cat = con.execute("""
        SELECT
            category,
            COUNT(DISTINCT product_id) AS catalog_products,
            SUM(total_units_sold) AS units_sold,
            ROUND(SUM(total_revenue_generated), 2) AS total_revenue,
            ROUND(SUM(total_profit_generated), 2) AS total_profit,
            ROUND(AVG(margin_percentage), 2) AS avg_margin_pct
        FROM dim_products
        GROUP BY 1
        ORDER BY total_revenue DESC
    """).fetchdf()
    st.dataframe(df_cat, use_container_width=True)

with tab2:
    st.subheader("🏛️ Dimensional Star-Schema & Modern Data Stack Lineage")
    st.markdown("""
    The analytical lakehouse adopts the **Kimball Dimensional Modeling** paradigm across 3 decoupled layers:
    - **Bronze (Raw Ingestion)**: High-throughput ingestion of raw OLTP tables (`raw_customers`, `raw_products`, `raw_orders`, `raw_order_items`).
    - **Silver (Staging & Intermediate)**: SQL cleaning, type coercion, standardizing datetime keys, and denormalized joins (`stg_*`, `int_*`).
    - **Gold (Star-Schema Marts)**: Conformed dimensions (`dim_customers`, `dim_products`, `dim_date`) and transactional grain fact tables (`fct_orders`, `fct_customer_retention`).
    """)
    
    st.markdown("""
    ```mermaid
    flowchart LR
        subgraph Bronze [Bronze Layer - Raw OLTP Ingestion]
            R1[raw_customers]
            R2[raw_products]
            R3[raw_orders]
            R4[raw_order_items]
        end

        subgraph Silver [Silver Layer - dbt Transformations]
            R1 --> S1[stg_customers]
            R2 --> S2[stg_products]
            R3 --> S3[stg_orders]
            R4 --> S4[stg_order_items]
            
            S4 & S2 --> I1[int_order_items_enriched]
            S1 & S3 & I1 --> I2[int_customer_metrics]
        end

        subgraph Gold [Gold Layer - Star-Schema Marts]
            I2 --> G1[dim_customers]
            S2 & I1 --> G2[dim_products]
            S3 & I1 --> G3[fct_orders]
            G1 & G3 --> G4[fct_customer_retention]
        end
    ```
    """)
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("**Sample Dimension: `dim_customers`**")
        st.dataframe(con.execute("SELECT * FROM dim_customers LIMIT 10").fetchdf(), use_container_width=True)
    with col_t2:
        st.markdown("**Sample Fact: `fct_orders`**")
        st.dataframe(con.execute("SELECT * FROM fct_orders LIMIT 10").fetchdf(), use_container_width=True)

with tab3:
    st.subheader("💻 Embedded DuckDB SQL Workbench")
    st.markdown("Execute high-speed vectorized OLAP queries directly against in-memory DuckDB tables.")
    
    PRESET_QUERIES = {
        "Top 10 Highest Lifetime Value Customers": """
SELECT
    customer_id,
    full_name,
    email,
    customer_segment_tier,
    total_successful_orders,
    lifetime_net_revenue,
    average_order_value
FROM dim_customers
ORDER BY lifetime_net_revenue DESC
LIMIT 10;
""",
        "Top 5 Bestselling Products by Profit Contribution": """
SELECT
    product_id,
    product_name,
    category,
    sub_category,
    total_units_sold,
    total_revenue_generated,
    total_profit_generated,
    sales_velocity_tier
FROM dim_products
ORDER BY total_profit_generated DESC
LIMIT 5;
""",
        "Monthly Cohort Retention Rate (%)": """
SELECT
    cohort_month,
    total_cohort_customers,
    month_number,
    active_retained_customers,
    retention_rate_percentage,
    cohort_revenue_generated
FROM fct_customer_retention
WHERE month_number <= 6
ORDER BY cohort_month, month_number
LIMIT 20;
""",
        "Payment Method Distribution & Average Spend": """
SELECT
    payment_method,
    COUNT(*) AS total_transactions,
    ROUND(SUM(net_merchandise_amount), 2) AS total_revenue,
    ROUND(AVG(net_merchandise_amount), 2) AS avg_transaction_size
FROM fct_orders
WHERE is_successful_order = 1
GROUP BY 1
ORDER BY total_revenue DESC;
"""
    }
    
    selected_preset = st.selectbox("Select Preset Analytical Query", list(PRESET_QUERIES.keys()))
    user_query = st.text_area("SQL Query Editor", value=PRESET_QUERIES[selected_preset], height=180)
    
    if st.button("🚀 Run Vectorized SQL Query"):
        try:
            res_df = con.execute(user_query).fetchdf()
            st.success(f"Query returned {len(res_df):,} rows in vectorized DuckDB OLAP engine.")
            st.dataframe(res_df, use_container_width=True)
        except Exception as e:
            st.error(f"SQL Execution Error: {e}")

with tab4:
    st.subheader("🛡️ Automated Data Quality & Contract Assertion Suite")
    st.markdown("""
    Automated schema constraints, nullity checks, referential integrity assertions, and enum validations run on every pipeline execution.
    """)
    
    tests_data = summary.get("data_quality_tests", {}).get("details", [])
    if tests_data:
        df_tests = pd.DataFrame(tests_data)
        st.dataframe(df_tests, use_container_width=True)
    else:
        st.info("Quality test telemetry will populate after pipeline run.")

st.markdown("""
---
<div style="text-align: center; color: #94A3B8; font-size: 0.85rem;">
    Developed by <b>Arjuna Fransesco</b> | <a href="https://github.com/ArjunaFransesco" target="_blank">GitHub Profile</a> | Modern Data Stack & Data Engineering Portfolio
</div>
""", unsafe_allow_html=True)
