import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
fake = Faker()

def generate_customers(n=1000):
    """Generate fake customer data"""
    customers = []
    countries = ['USA', 'UK', 'Germany', 'France', 'Japan', 'Australia', 'Canada']
    for i in range(n):
        signup_date = fake.date_between(start_date='-3y', end_date='-1m')
        customers.append({
            'customer_id': i + 1,
            'customer_name': fake.name(),
            'email': fake.email(),
            'country': random.choice(countries),
            'signup_date': signup_date,
            'is_active': random.random() > 0.1,
            'created_at': datetime.now()
        })
    return pd.DataFrame(customers)

def generate_products(n=200):
    """Generate fake product data"""
    categories = {
        'Electronics': ['Phones', 'Laptops', 'Tablets', 'Accessories'],
        'Clothing': ['Shirts', 'Pants', 'Shoes', 'Accessories'],
        'Home': ['Furniture', 'Decor', 'Kitchen', 'Garden'],
        'Books': ['Fiction', 'Non-fiction', 'Educational', 'Comics'],
        'Sports': ['Equipment', 'Apparel', 'Footwear', 'Accessories']
    }
    products = []
    for i in range(n):
        category = random.choice(list(categories.keys()))
        subcategory = random.choice(categories[category])
        price = round(random.uniform(10, 1000), 2)
        cost = round(price * random.uniform(0.3, 0.7), 2)
        products.append({
            'product_id': i + 1,
            'product_name': fake.catch_phrase(),
            'category': category,
            'subcategory': subcategory,
            'price': price,
            'cost': cost,
            'stock_quantity': random.randint(0, 500),
            'supplier_id': random.randint(1, 20),
            'is_discontinued': random.random() < 0.05
        })
    return pd.DataFrame(products)

def generate_orders(customers_df, products_df, n=5000):
    """Generate fake order data with order items"""
    orders = []
    order_items = []
    payment_methods = ['Credit Card', 'PayPal', 'Bank Transfer', 'Cash', 'Crypto']
    statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled', 'returned']
    active_customers = customers_df[customers_df['is_active']]['customer_id'].tolist()
    
    for i in range(n):
        customer_id = random.choice(active_customers)
        customer = customers_df[customers_df['customer_id'] == customer_id].iloc[0]
        order_date = fake.date_between(start_date=customer['signup_date'], end_date='today')
        
        order_total = 0
        num_items = random.randint(1, 5)
        discount_amount = 0
        
        for _ in range(num_items):
            product = products_df.sample(1).iloc[0]
            quantity = random.randint(1, 3)
            unit_price = product['price']
            discount_percent = random.choice([0, 0, 0, 5, 10, 15, 20])
            item_total = unit_price * quantity * (1 - discount_percent/100)
            order_total += item_total
            
            order_items.append({
                'order_id': i + 1,
                'product_id': product['product_id'],
                'quantity': quantity,
                'unit_price': unit_price,
                'discount_percent': discount_percent
            })
        
        if random.random() < 0.3:
            discount_amount = round(order_total * random.uniform(0.05, 0.15), 2)
            order_total -= discount_amount
        
        orders.append({
            'order_id': i + 1,
            'customer_id': customer_id,
            'order_date': order_date,
            'total_amount': round(order_total, 2),
            'discount_amount': discount_amount,
            'status': random.choice(statuses),
            'payment_method': random.choice(payment_methods),
            'shipping_address': fake.address().replace('\n', ', '),
            'created_at': datetime.now()
        })
    
    return pd.DataFrame(orders), pd.DataFrame(order_items)

def save_to_files(customers_df, products_df, orders_df, order_items_df):
    """Save dataframes to CSV files"""
    data_path = 'setup/sample_data'
    os.makedirs(data_path, exist_ok=True)
    
    customers_df.to_csv(f'{data_path}/customers.csv', index=False)
    products_df.to_csv(f'{data_path}/products.csv', index=False)
    orders_df.to_csv(f'{data_path}/orders.csv', index=False)
    order_items_df.to_csv(f'{data_path}/order_items.csv', index=False)
    
    print(f"✅ Sample data files created in {data_path}")

if __name__ == "__main__":
    print("🔄 Generating mock data...")
    
    customers_df = generate_customers(1000)
    products_df = generate_products(200)
    orders_df, order_items_df = generate_orders(customers_df, products_df, 5000)
    
    save_to_files(customers_df, products_df, orders_df, order_items_df)
    
    print("\n📊 Data Generation Summary:")
    print(f"  • Customers: {len(customers_df):,}")
    print(f"  • Products: {len(products_df):,}")
    print(f"  • Orders: {len(orders_df):,}")
    print(f"  • Order Items: {len(order_items_df):,}")
    print("\n✅ Mock data generated successfully!")