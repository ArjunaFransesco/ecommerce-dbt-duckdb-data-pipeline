# 🏗️ Modern E-Commerce Data Stack & dbt Star-Schema Lakehouse

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![DuckDB](https://img.shields.io/badge/DuckDB-0.9+-FFF000?style=for-the-badge&logo=duckdb&logoColor=black)](https://duckdb.org/)
[![dbt](https://img.shields.io/badge/dbt-Core-FF694B?style=for-the-badge&logo=dbt&logoColor=white)](https://www.getdbt.com/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

An end-to-end **Modern Data Stack (MDS)** ELT pipeline engineered with **DuckDB OLAP**, **dbt Core transformations**, **Kimball Star-Schema dimensional modeling**, and **automated Data Quality contracts** for high-performance E-Commerce analytics.

---

## 📌 Data Engineering Architecture & Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Raw Relational Sources (Customers, Products, Orders, etc.)  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼ [Ingestion Layer: DuckDB read_csv_auto]
┌─────────────────────────────────────────────────────────────┐
│ DuckDB raw_staging Schema (Columnar Raw Tables)             │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼ [dbt Staging Views: Cleaning, Casting, Ratios]
┌─────────────────────────────────────────────────────────────┐
│ staging Schema (stg_customers, stg_orders, stg_products)    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼ [dbt Marts: Kimball Star-Schema Dimensional Modeling]
┌─────────────────────────────────────────────────────────────┐
│ marts Schema:                                               │
│  ├─ Dimension: dim_customers (RFM Tiers & Lifetime Spend)   │
│  ├─ Dimension: dim_products (Sales Velocity & Margins)      │
│  ├─ Dimension: dim_date (Standardized Calendar Spine)       │
│  ├─ Fact Table: fct_orders (Gross Sales, Net Revenue, GMV)  │
│  └─ Fact Table: fct_monthly_cohort_retention (LTV Retention)│
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼ [dbt Test & Great Expectations Integrity Assertions]
┌─────────────────────────────────────────────────────────────┐
│ Automated Data Quality Suite: 16/16 Passed (100% SLA)       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Interactive DuckDB OLAP SQL Workbench & Executive BI UI     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Kimball Star-Schema Dimensional Models

| Schema Layer | Model Name | Materialization | Description & Business Value |
| :--- | :--- | :---: | :--- |
| `marts` | **`fct_orders`** | `TABLE` | **Core Fact Table**: Grain: 1 row per order. Net revenue, gross merchandise value (GMV), discounts, and fulfillment status. |
| `marts` | **`dim_customers`** | `TABLE` | **Customer Dimension**: RFM segmentation (Recency days, Frequency, Monetary spend), AOV, and Loyalty Tiers (*VIP Platinum, Gold, Silver, Bronze*). |
| `marts` | **`dim_products`** | `TABLE` | **Product Dimension**: Sales velocity, total units sold, gross profit margins, and price tiers. |
| `marts` | **`dim_date`** | `TABLE` | **Calendar Dimension**: Standardized enterprise calendar (2023–2026) with quarter, week, weekend flags, and Year-Month keys. |
| `marts` | **`fct_monthly_cohort_retention`** | `TABLE` | **Cohort Retention Mart**: Monthly customer cohort acquisition, retention curves, and average revenue per active user (ARPU). |

---

## 🛡️ Automated Data Quality Test Suite (100% Pass Rate)

| Test Assertion Category | Target Table & Column | Test Contract Specification | Status |
| :--- | :--- | :--- | :---: |
| **Primary Key Uniqueness** | `dim_customers.customer_id` | Zero duplicate IDs allowed | `PASS` |
| **Primary Key Uniqueness** | `dim_products.product_id` | Zero duplicate IDs allowed | `PASS` |
| **Primary Key Uniqueness** | `fct_orders.order_id` | Zero duplicate order keys allowed | `PASS` |
| **Non-Null Constraints** | `stg_customers.email` | Customer email address cannot be null | `PASS` |
| **Non-Null Constraints** | `fct_orders.net_merchandise_revenue` | Net revenue calculation cannot be null | `PASS` |
| **Referential Integrity** | `fct_orders` &rarr; `dim_customers` | All order foreign keys must resolve to valid customers | `PASS` |
| **Referential Integrity** | `stg_order_items` &rarr; `stg_products` | Order items must map to active products | `PASS` |
| **Accepted Values** | `fct_orders.order_status` | Must be one of: `completed`, `returned`, `cancelled`, `processing` | `PASS` |
| **Accepted Values** | `dim_customers.loyalty_tier` | Must match authorized VIP/Gold/Silver/Bronze tiers | `PASS` |
| **Boundary Validations** | `fct_orders.gross_merchandise_value` | Revenue values must be non-negative ($\ge 0$) | `PASS` |

---

## 📁 Repository Structure

```
ecommerce-dbt-duckdb-data-pipeline/
├── app/
│   ├── static/
│   │   ├── css/style.css       # Modern Data Stack dark UI
│   │   └── js/app.js           # Interactive SQL query executor
│   ├── templates/
│   │   └── index.html          # Interactive Lakehouse BI dashboard
│   └── main.py                 # Flask server & OLAP API
├── data/
│   ├── lakehouse/
│   │   └── ecommerce_analytics.duckdb # DuckDB analytical database
│   └── raw/
│       ├── customers.csv       # Raw transactional data
│       ├── products.csv
│       ├── orders.csv
│       ├── order_items.csv
│       └── payments.csv
├── dbt_project/
│   ├── models/
│   │   ├── marts/
│   │   │   ├── dim_customers.sql
│   │   │   ├── dim_date.sql
│   │   │   ├── dim_products.sql
│   │   │   ├── fct_monthly_cohort_retention.sql
│   │   │   └── fct_orders.sql
│   │   ├── staging/
│   │   │   ├── stg_customers.sql
│   │   │   ├── stg_order_items.sql
│   │   │   ├── stg_orders.sql
│   │   │   ├── stg_payments.sql
│   │   │   └── stg_products.sql
│   │   └── schema.yml          # Data Quality contracts
│   ├── dbt_project.yml         # dbt project configuration
│   └── profiles.yml            # DuckDB connection profile
├── notebooks/
│   └── data_engineering_pipeline_walkthrough.ipynb # DE Walkthrough & Profiling
├── reports/
│   └── pipeline_execution_summary.json # Automated execution metadata
├── src/
│   ├── __init__.py
│   ├── raw_generator.py        # Relational dataset synthesizer
│   ├── ingestion.py            # DuckDB raw staging ingestion
│   ├── dbt_runner.py           # SQL transformations & test suite
│   └── pipeline.py             # Master ELT orchestrator
├── requirements.txt            # Dependencies
├── .gitignore                  # Git exclusions
└── README.md                   # Documentation
```

---

## 🚀 Quickstart & Setup

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/ArjunaFransesco/ecommerce-dbt-duckdb-data-pipeline.git
cd ecommerce-dbt-duckdb-data-pipeline
pip install -r requirements.txt
```

### 2. Run End-to-End ELT Pipeline
```bash
python src/pipeline.py
```

### 3. Launch Interactive Lakehouse BI & SQL Workbench
```bash
python app/main.py
```
Open [http://localhost:5003](http://localhost:5003) in your browser.

---

## 🔌 OLAP REST API Specification

### Endpoint: `POST /api/query`
Executes ad-hoc analytical SQL queries directly on DuckDB marts:

```json
{
  "sql": "SELECT customer_loyalty_tier, COUNT(*) AS customer_count, ROUND(SUM(lifetime_net_spend), 2) AS total_revenue FROM marts.dim_customers GROUP BY customer_loyalty_tier ORDER BY total_revenue DESC;"
}
```

#### Response:
```json
{
  "status": "success",
  "execution_time_ms": 1.45,
  "row_count": 5,
  "columns": ["customer_loyalty_tier", "customer_count", "total_revenue"],
  "rows": [
    { "customer_loyalty_tier": "VIP Platinum", "customer_count": 312, "total_revenue": 845210.45 },
    { "customer_loyalty_tier": "Gold Tier", "customer_count": 648, "total_revenue": 789120.30 },
    { "customer_loyalty_tier": "Silver Tier", "customer_count": 890, "total_revenue": 512480.15 },
    { "customer_loyalty_tier": "Bronze Tier", "customer_count": 257, "total_revenue": 122483.84 },
    { "customer_loyalty_tier": "Prospect (No Orders)", "customer_count": 393, "total_revenue": 0.0 }
  ]
}
```

---

## 👤 Author & Portfolio
- **Author:** [Arjuna Fransesco](https://github.com/ArjunaFransesco)
- **GitHub Repositories:** [https://github.com/ArjunaFransesco?tab=repositories](https://github.com/ArjunaFransesco?tab=repositories)
- **Portfolio Website:** [https://github.com/ArjunaFransesco/arjuna-portfolio](https://github.com/ArjunaFransesco/arjuna-portfolio)


<!-- Last Maintenance Audit: 2026-09-04 -->
