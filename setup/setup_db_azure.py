"""
Database Reset Script - Azure Compatible Version
This script works with both local Docker PostgreSQL and Azure PostgreSQL
"""

import pandas as pd
from sqlalchemy import create_engine, text
import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection - Use environment variable or default to local
db_connection = os.getenv('DB_CONNECTION_STRING', 
                          'postgresql://postgressadmin:wf**F!$3dGdf14@copilot-workshop-db.postgres.database.azure.com:5432/workshop_db')

print(f"🔗 Connecting to database...")
print(f"   Using connection: {db_connection.split('@')[1] if '@' in db_connection else 'localhost'}")

try:
    engine = create_engine(db_connection)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("✅ Connection successful!\n")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\nTroubleshooting tips:")
    print("1. Check if database server is running")
    print("2. Verify credentials in .env file")
    print("3. Check firewall rules (for Azure)")
    print("4. Ensure SSL is configured (for Azure: add ?sslmode=require)")
    sys.exit(1)

print("🔄 Resetting and reloading database...\n")

# Step 1: Regenerate mock data
print("1. Generating fresh mock data...")
subprocess.run([sys.executable, 'setup/generate_mock_data.py'], check=True)

# Step 2: Load data from CSV files
print("\n2. Loading data from CSV files...")
data_path = 'setup/sample_data'
try:
    customers = pd.read_csv(f'{data_path}/customers.csv')
    products = pd.read_csv(f'{data_path}/products.csv')
    orders = pd.read_csv(f'{data_path}/orders.csv')
    order_items = pd.read_csv(f'{data_path}/order_items.csv')
    print("  ✅ All CSV files loaded successfully.")
except FileNotFoundError as e:
    print(f"❌ CSV file not found: {e}. Aborting.")
    sys.exit(1)

# Step 3: Create schemas
print("\n3. Creating schemas...")
try:
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS analytics"))
    print("  ✅ Schemas created successfully.")
except Exception as e:
    print(f"⚠️  Schema creation warning: {e}")

# Step 4: Drop and recreate tables with correct schema
print("\n4. Dropping and recreating tables with correct schema...")
try:
    with engine.begin() as conn:
        # Drop tables in correct order (due to foreign keys)
        conn.execute(text("DROP TABLE IF EXISTS raw.order_items CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS raw.orders CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS raw.products CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS raw.customers CASCADE"))
        
        # Recreate customers table
        conn.execute(text("""
            CREATE TABLE raw.customers (
                customer_id SERIAL PRIMARY KEY,
                customer_name VARCHAR(255),
                email VARCHAR(255),
                country VARCHAR(100),
                signup_date DATE,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Recreate products table
        conn.execute(text("""
            CREATE TABLE raw.products (
                product_id SERIAL PRIMARY KEY,
                product_name VARCHAR(255),
                category VARCHAR(100),
                subcategory VARCHAR(100),
                price DECIMAL(10,2),
                cost DECIMAL(10,2),
                stock_quantity INTEGER,
                supplier_id INTEGER,
                is_discontinued BOOLEAN DEFAULT false
            )
        """))
        
        # Recreate orders table
        conn.execute(text("""
            CREATE TABLE raw.orders (
                order_id SERIAL PRIMARY KEY,
                customer_id INTEGER REFERENCES raw.customers(customer_id),
                order_date DATE,
                total_amount DECIMAL(10,2),
                discount_amount DECIMAL(10,2) DEFAULT 0,
                status VARCHAR(50),
                payment_method VARCHAR(50),
                shipping_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Recreate order_items table
        conn.execute(text("""
            CREATE TABLE raw.order_items (
                order_item_id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES raw.orders(order_id),
                product_id INTEGER REFERENCES raw.products(product_id),
                quantity INTEGER,
                unit_price DECIMAL(10,2),
                discount_percent DECIMAL(5,2) DEFAULT 0
            )
        """))
        
        # Create indexes
        conn.execute(text("CREATE INDEX idx_orders_customer_id ON raw.orders(customer_id)"))
        conn.execute(text("CREATE INDEX idx_orders_date ON raw.orders(order_date)"))
        conn.execute(text("CREATE INDEX idx_order_items_order_id ON raw.order_items(order_id)"))
        conn.execute(text("CREATE INDEX idx_order_items_product_id ON raw.order_items(product_id)"))
        
    print("  ✅ Tables recreated successfully.")
except Exception as e:
    print(f"❌ Could not recreate tables: {e}")
    sys.exit(1)

# Step 5: Load fresh data into PostgreSQL
print("\n5. Loading fresh data into database...")
try:
    with engine.begin() as conn:
        # Load customers
        customers.to_sql('customers', conn, schema='raw', if_exists='append', index=False, method='multi')
        max_id = customers['customer_id'].max()
        conn.execute(text(f"SELECT setval('raw.customers_customer_id_seq', {max_id})"))
        print(f"  ✅ Loaded {len(customers):,} customers")
        
        # Load products
        products.to_sql('products', conn, schema='raw', if_exists='append', index=False, method='multi')
        max_id = products['product_id'].max()
        conn.execute(text(f"SELECT setval('raw.products_product_id_seq', {max_id})"))
        print(f"  ✅ Loaded {len(products):,} products")
        
        # Load orders
        orders.to_sql('orders', conn, schema='raw', if_exists='append', index=False, method='multi')
        max_id = orders['order_id'].max()
        conn.execute(text(f"SELECT setval('raw.orders_order_id_seq', {max_id})"))
        print(f"  ✅ Loaded {len(orders):,} orders")
        
        # Load order_items (no ID in CSV, auto-generated)
        order_items.to_sql('order_items', conn, schema='raw', if_exists='append', index=False, method='multi')
        print(f"  ✅ Loaded {len(order_items):,} order items")
        
except Exception as e:
    print(f"❌ Data load failed: {e}")
    sys.exit(1)

# Step 6: Recreate analytics views
print("\n6. Recreating analytics views...")
try:
    with engine.begin() as conn:
        # Customer Summary View
        conn.execute(text("""
            CREATE OR REPLACE VIEW analytics.customer_summary AS
            SELECT 
                c.customer_id,
                c.customer_name,
                c.country,
                COUNT(DISTINCT o.order_id) as total_orders,
                COALESCE(SUM(o.total_amount), 0) as lifetime_value,
                COALESCE(AVG(o.total_amount), 0) as avg_order_value,
                MAX(o.order_date) as last_order_date,
                MIN(o.order_date) as first_order_date
            FROM raw.customers c
            LEFT JOIN raw.orders o ON c.customer_id = o.customer_id
            GROUP BY c.customer_id, c.customer_name, c.country
        """))
        
        # Product Performance View
        conn.execute(text("""
            CREATE OR REPLACE VIEW analytics.product_performance AS
            SELECT 
                p.product_id,
                p.product_name,
                p.category,
                p.price,
                COUNT(DISTINCT oi.order_id) as times_ordered,
                COALESCE(SUM(oi.quantity), 0) as total_quantity_sold,
                COALESCE(SUM(oi.quantity * oi.unit_price), 0) as total_revenue
            FROM raw.products p
            LEFT JOIN raw.order_items oi ON p.product_id = oi.product_id
            GROUP BY p.product_id, p.product_name, p.category, p.price
        """))
        
        # Monthly Sales View
        conn.execute(text("""
            CREATE OR REPLACE VIEW analytics.monthly_sales AS
            SELECT 
                DATE_TRUNC('month', o.order_date) as month,
                COUNT(DISTINCT o.order_id) as order_count,
                COUNT(DISTINCT o.customer_id) as unique_customers,
                SUM(o.total_amount) as total_revenue,
                AVG(o.total_amount) as avg_order_value
            FROM raw.orders o
            GROUP BY DATE_TRUNC('month', o.order_date)
            ORDER BY month DESC
        """))
        
    print("  ✅ Analytics views recreated.")
except Exception as e:
    print(f"❌ Failed to create views: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✅ SUCCESS! Database has been reset and reloaded.")
print("="*60)
print(f"\n📊 Summary:")
print(f"   • Customers: {len(customers):,}")
print(f"   • Products: {len(products):,}")
print(f"   • Orders: {len(orders):,}")
print(f"   • Order Items: {len(order_items):,}")
print(f"   • Analytics Views: 3")
print("\n🎉 Ready for exercises!")
