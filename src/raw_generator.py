"""
Synthetic Relational E-Commerce Transaction Generator.
Produces normalized transactional tables: customers, products, orders, order_items, payments.
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def generate_ecommerce_raw_data(
    n_customers: int = 2500,
    n_products: int = 150,
    n_orders: int = 8000,
    output_dir: str = "data/raw",
    random_state: int = 42
):
    np.random.seed(random_state)
    os.makedirs(output_dir, exist_ok=True)
    print(f"[+] Generating raw relational E-Commerce datasets in {output_dir}...")

    # 1. Customers Table
    first_names = ["James", "Emma", "Michael", "Sophia", "Daniel", "Olivia", "Alexander", "Isabella", "William", "Mia",
                   "David", "Emily", "Joseph", "Charlotte", "Gabriel", "Amelia", "Lucas", "Harper", "Henry", "Evelyn"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                  "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
    states = ["NY", "CA", "IL", "TX", "AZ", "PA", "TX", "CA", "TX", "CA"]
    segments = ["Consumer", "SMB", "Enterprise"]
    segment_weights = [0.70, 0.22, 0.08]

    customer_records = []
    base_date = datetime(2023, 1, 1)

    for cid in range(1, n_customers + 1):
        fn = np.random.choice(first_names)
        ln = np.random.choice(last_names)
        loc_idx = np.random.randint(0, len(cities))
        reg_days = np.random.randint(0, 730)
        reg_date = base_date + timedelta(days=reg_days)
        segment = np.random.choice(segments, p=segment_weights)

        customer_records.append({
            "customer_id": cid,
            "first_name": fn,
            "last_name": ln,
            "email": f"{fn.lower()}.{ln.lower()}{cid}@example.com",
            "city": cities[loc_idx],
            "state": states[loc_idx],
            "country": "United States",
            "segment": segment,
            "registration_date": reg_date.strftime("%Y-%m-%d")
        })

    df_customers = pd.DataFrame(customer_records)
    customers_path = os.path.join(output_dir, "customers.csv")
    df_customers.to_csv(customers_path, index=False)
    print(f"  [✓] Customers: {len(df_customers)} records -> {customers_path}")

    # 2. Products Table
    categories = {
        "Electronics": ["Smartphone Pro", "Noise-Cancelling Headphones", "4K Ultra Monitor", "Wireless Keyboard", "USB-C Fast Charger", "Smartwatch Elite"],
        "Apparel": ["Merino Wool Sweater", "Slim-fit Chinos", "Waterproof Shell Jacket", "Running Performance Shoes", "Cotton Graphic Tee"],
        "Home & Kitchen": ["Espresso Coffee Machine", "Stainless Steel Cookware", "Air Purifier HEPA", "Cast Iron Skillet", "Smart LED Desk Lamp"],
        "Health & Beauty": ["Sonic Electric Toothbrush", "Hydrating Facial Serum", "Organic Vitamin Complex", "Mineral Sunscreen SPF50"],
        "Sports & Outdoors": ["Yoga Mat Non-Slip", "Adjustable Dumbbell Set", "Insulated Hydro Flask", "Trail Running Hydration Pack"]
    }

    product_records = []
    pid = 1
    for cat, items in categories.items():
        for item in items:
            for variant in ["Standard", "Pro", "Plus"]:
                unit_price = round(float(np.random.uniform(25.0, 450.0)), 2)
                cost_margin = np.random.uniform(0.40, 0.70)
                cost_price = round(unit_price * cost_margin, 2)

                product_records.append({
                    "product_id": pid,
                    "product_name": f"{item} ({variant})",
                    "category": cat,
                    "unit_price": unit_price,
                    "cost_price": cost_price,
                    "is_active": True
                })
                pid += 1
                if pid > n_products:
                    break
        if pid > n_products:
            break

    df_products = pd.DataFrame(product_records)
    products_path = os.path.join(output_dir, "products.csv")
    df_products.to_csv(products_path, index=False)
    print(f"  [✓] Products: {len(df_products)} records -> {products_path}")

    # 3. Orders & Order Items Table
    order_statuses = ["completed", "completed", "completed", "completed", "returned", "cancelled", "processing"]
    devices = ["Mobile", "Desktop", "Tablet"]
    device_weights = [0.58, 0.34, 0.08]

    # Create fast product lookup dict
    prod_dict = {
        row["product_id"]: row for _, row in df_products.iterrows()
    }

    order_records = []
    item_records = []
    payment_records = []

    order_item_id = 1
    payment_id = 1

    for oid in range(1, n_orders + 1):
        cid = np.random.randint(1, n_customers + 1)
        cust_reg = datetime.strptime(df_customers.loc[cid - 1, "registration_date"], "%Y-%m-%d")
        days_after_reg = np.random.randint(0, 365)
        order_time = cust_reg + timedelta(days=days_after_reg, hours=np.random.randint(0, 24), minutes=np.random.randint(0, 60))
        status = np.random.choice(order_statuses)
        device = np.random.choice(devices, p=device_weights)
        shipping_cost = float(np.random.choice([0.0, 5.99, 9.99, 14.99], p=[0.45, 0.35, 0.15, 0.05]))

        # Generate 1 to 4 items per order
        n_items = np.random.choice([1, 2, 3, 4], p=[0.55, 0.28, 0.12, 0.05])
        chosen_pids = np.random.choice(df_products["product_id"].values, size=n_items, replace=False)

        order_gross_amount = 0.0
        for p in chosen_pids:
            prod_row = prod_dict[p]
            qty = int(np.random.choice([1, 2, 3], p=[0.80, 0.15, 0.05]))
            u_price = float(prod_row["unit_price"])
            discount_pct = float(np.random.choice([0.0, 0.05, 0.10, 0.15, 0.20], p=[0.60, 0.15, 0.12, 0.08, 0.05]))
            item_total = (u_price * (1 - discount_pct)) * qty
            order_gross_amount += item_total

            item_records.append({
                "order_item_id": order_item_id,
                "order_id": oid,
                "product_id": int(p),
                "quantity": qty,
                "unit_price": u_price,
                "discount_percent": discount_pct
            })
            order_item_id += 1

        total_amount = round(order_gross_amount + shipping_cost, 2)

        order_records.append({
            "order_id": oid,
            "customer_id": cid,
            "order_status": status,
            "order_timestamp": order_time.strftime("%Y-%m-%d %H:%M:%S"),
            "device_type": device,
            "shipping_cost": shipping_cost
        })

        # Payment for order
        pay_method = np.random.choice(["Credit Card", "PayPal", "Apple Pay", "Crypto", "Bank Transfer"], p=[0.55, 0.25, 0.12, 0.05, 0.03])
        pay_status = "success" if status in ["completed", "processing", "returned"] else ("failed" if status == "cancelled" else "refunded")

        payment_records.append({
            "payment_id": payment_id,
            "order_id": oid,
            "payment_method": pay_method,
            "payment_status": pay_status,
            "amount": total_amount,
            "payment_timestamp": (order_time + timedelta(minutes=np.random.randint(1, 10))).strftime("%Y-%m-%d %H:%M:%S")
        })
        payment_id += 1

    df_orders = pd.DataFrame(order_records)
    orders_path = os.path.join(output_dir, "orders.csv")
    df_orders.to_csv(orders_path, index=False)
    print(f"  [✓] Orders: {len(df_orders)} records -> {orders_path}")

    df_items = pd.DataFrame(item_records)
    items_path = os.path.join(output_dir, "order_items.csv")
    df_items.to_csv(items_path, index=False)
    print(f"  [✓] Order Items: {len(df_items)} records -> {items_path}")

    df_payments = pd.DataFrame(payment_records)
    payments_path = os.path.join(output_dir, "payments.csv")
    df_payments.to_csv(payments_path, index=False)
    print(f"  [✓] Payments: {len(df_payments)} records -> {payments_path}")

    print("[+] All relational E-Commerce tables synthesized successfully!\n")


if __name__ == "__main__":
    generate_ecommerce_raw_data()
