"""
Raw E-Commerce OLTP Data Extraction and Bronze Lakehouse Generator
Generates transactional raw tables: customers, products, orders, and order_items.
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def generate_raw_ecommerce_data(
    n_customers: int = 1200,
    n_products: int = 150,
    n_orders: int = 8000,
    random_state: int = 42,
    output_dir: str = None
) -> Dict[str, pd.DataFrame]:
    """
    Synthesizes raw transactional e-commerce dataset for ELT lakehouse ingestion.
    """
    np.random.seed(random_state)
    start_date = datetime(2023, 1, 1)
    
    # 1. Customers Table
    first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Sam", "Chris", "Pat", "Riley", "Casey", "Avery", "Dakota", "Jamie"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    cities = ["Jakarta", "Surabaya", "Bandung", "Medan", "Semarang", "Singapore", "Kuala Lumpur", "Bangkok"]
    devices = ["iOS App", "Android App", "Web Desktop", "Mobile Safari", "Mobile Chrome"]
    
    customers = []
    for cid in range(1001, 1001 + n_customers):
        fn = np.random.choice(first_names)
        ln = np.random.choice(last_names)
        signup = start_date + timedelta(days=int(np.random.randint(0, 500)))
        customers.append({
            "customer_id": f"CUST_{cid}",
            "first_name": fn,
            "last_name": ln,
            "email": f"{fn.lower()}.{ln.lower()}{cid}@example.com",
            "city": np.random.choice(cities),
            "country": "Indonesia" if np.random.rand() < 0.85 else "Southeast Asia",
            "signup_timestamp": signup.strftime("%Y-%m-%d %H:%M:%S"),
            "device_preference": np.random.choice(devices)
        })
    df_customers = pd.DataFrame(customers)
    
    # 2. Products Table
    categories = {
        "Electronics": ["Smartphone", "Wireless Earbuds", "Smartwatch", "Mechanical Keyboard", "USB-C Hub", "Gaming Monitor"],
        "Apparel": ["Oversized Hoodie", "Slim Fit Chinos", "Graphic T-Shirt", "Sneakers", "Running Jacket"],
        "Home & Living": ["Ergonomic Chair", "Desk Mat", "Aroma Diffuser", "Ceramic Mug", "LED Desk Lamp"],
        "Beauty & Care": ["Sunscreen SPF50", "Hydrating Serum", "Clay Mask", "Hair Treatment Oil"]
    }
    
    products = []
    pid = 501
    for cat, subcats in categories.items():
        for sub in subcats:
            for variant in ["Standard", "Pro", "Lite", "Premium"]:
                cost = round(float(np.random.uniform(8.0, 180.0)), 2)
                margin = float(np.random.uniform(1.35, 2.2))
                retail = round(cost * margin, 2)
                products.append({
                    "product_id": f"PROD_{pid}",
                    "product_name": f"{sub} ({variant})",
                    "category": cat,
                    "sub_category": sub,
                    "cost_price": cost,
                    "retail_price": retail,
                    "is_active": 1 if np.random.rand() < 0.95 else 0
                })
                pid += 1
                if len(products) >= n_products:
                    break
    df_products = pd.DataFrame(products)
    
    # 3. Orders Table
    orders = []
    customer_ids = df_customers["customer_id"].values
    payment_methods = ["Credit Card", "E-Wallet (GoPay/OVO)", "Virtual Account Bank Transfer", "QRIS", "BNPL"]
    order_statuses = ["Completed", "Shipped", "Delivered", "Cancelled", "Returned"]
    status_weights = [0.72, 0.12, 0.08, 0.05, 0.03]
    
    for oid in range(20001, 20001 + n_orders):
        cid = np.random.choice(customer_ids)
        cust_signup = datetime.strptime(df_customers.loc[df_customers["customer_id"] == cid, "signup_timestamp"].values[0], "%Y-%m-%d %H:%M:%S")
        days_after_signup = int(np.random.exponential(scale=90))
        order_time = cust_signup + timedelta(days=days_after_signup, hours=int(np.random.randint(0, 24)))
        
        status = np.random.choice(order_statuses, p=status_weights)
        shipping_cost = 0.0 if np.random.rand() < 0.4 else round(float(np.random.uniform(2.5, 9.0)), 2)
        
        orders.append({
            "order_id": f"ORD_{oid}",
            "customer_id": cid,
            "order_timestamp": order_time.strftime("%Y-%m-%d %H:%M:%S"),
            "order_status": status,
            "payment_method": np.random.choice(payment_methods),
            "shipping_cost": shipping_cost
        })
    df_orders = pd.DataFrame(orders)
    
    # 4. Order Items Table
    order_items = []
    product_ids = df_products["product_id"].values
    prod_prices = dict(zip(df_products["product_id"], df_products["retail_price"]))
    
    item_id = 100001
    for _, ord_row in df_orders.iterrows():
        n_items = int(np.random.choice([1, 2, 3, 4], p=[0.55, 0.28, 0.12, 0.05]))
        chosen_prods = np.random.choice(product_ids, size=n_items, replace=False)
        
        for pid in chosen_prods:
            qty = int(np.random.choice([1, 2, 3], p=[0.75, 0.20, 0.05]))
            unit_p = prod_prices[pid]
            discount = round(unit_p * qty * float(np.random.choice([0.0, 0.05, 0.10, 0.15], p=[0.70, 0.15, 0.10, 0.05])), 2)
            
            order_items.append({
                "item_id": f"ITEM_{item_id}",
                "order_id": ord_row["order_id"],
                "product_id": pid,
                "quantity": qty,
                "unit_price": unit_p,
                "discount_amount": discount
            })
            item_id += 1
            
    df_order_items = pd.DataFrame(order_items)
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        df_customers.to_csv(os.path.join(output_dir, "raw_customers.csv"), index=False)
        df_products.to_csv(os.path.join(output_dir, "raw_products.csv"), index=False)
        df_orders.to_csv(os.path.join(output_dir, "raw_orders.csv"), index=False)
        df_order_items.to_csv(os.path.join(output_dir, "raw_order_items.csv"), index=False)
        print(f"[+] Raw data extracted & saved to {output_dir}")
        
    return {
        "customers": df_customers,
        "products": df_products,
        "orders": df_orders,
        "order_items": df_order_items
    }
