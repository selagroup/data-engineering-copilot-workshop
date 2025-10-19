import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import psycopg2
from sqlalchemy import create_engine

fake = Faker()

def generate_customers(n=1000):
    customers = []
    for _ in range(n):
        customers.append({
            'customer_name': fake.name(),
            'email': fake.email(),
            'country': fake.country(),
            'created_at': fake.date_time_between(start_date='-2y', end_date='now')
        })
    return pd.DataFrame(customers)

def generate_orders(customer_ids, n=5000):
    orders = []
    for _ in range(n):
        orders.append({
            'customer_id': random.choice(customer_ids),
            'order_date': fake.date_between(start_date='-1y', end_date='today'),
            'total_amount': round(random.uniform(10, 1000), 2),
            'status': random.choice(['pending', 'completed', 'cancelled', 'shipped'])
        })
    return pd.DataFrame(orders)

def generate_products(n=200):
    categories = ['Electronics', 'Clothing', 'Food', 'Books', 'Home']
    products = []
    for _ in range(n):
        products.append({
            'product_name': fake.catch_phrase(),
            'category': random.choice(categories),
            'price': round(random.uniform(5, 500), 2),
            'stock_quantity': random.randint(0, 1000)
        })
    return pd.DataFrame(products)

if __name__ == "__main__":
    # Generate data
    customers_df = generate_customers()
    orders_df = generate_orders(customers_df.index + 1, 5000)
    products_df = generate_products()
    
    # Save to CSV
    customers_df.to_csv('setup/sample_data/customers.csv', index=False)
    orders_df.to_csv('setup/sample_data/orders.csv', index=False)
    products_df.to_csv('setup/sample_data/products.csv', index=False)
    
    # Also create a parquet file for PySpark demo
    transactions_df = orders_df.merge(
        customers_df.reset_index().rename(columns={'index': 'customer_id'}),
        on='customer_id'
    )
    transactions_df.to_parquet('setup/sample_data/transactions.parquet')
    
    print("✅ Mock data generated successfully!")