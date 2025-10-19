# Create a file: test_db.py
import pandas as pd
from sqlalchemy import create_engine

# Create connection
engine = create_engine('postgresql://dataeng:copilot123@localhost:5432/workshop_db')

# Test queries
print("Testing database connection...\n")

# Check schemas
schemas = pd.read_sql("""
    SELECT schema_name 
    FROM information_schema.schemata 
    WHERE schema_name IN ('raw', 'staging', 'analytics')
""", engine)
print("Schemas created:", schemas['schema_name'].tolist())

# Check tables
tables = pd.read_sql("""
    SELECT table_schema, table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'raw'
""", engine)
print("\nTables in 'raw' schema:", tables['table_name'].tolist())

# Count records
customers = pd.read_sql("SELECT COUNT(*) as count FROM raw.customers", engine)
print(f"\nCustomers: {customers['count'][0]:,}")

orders = pd.read_sql("SELECT COUNT(*) as count FROM raw.orders", engine)
print(f"Orders: {orders['count'][0]:,}")

products = pd.read_sql("SELECT COUNT(*) as count FROM raw.products", engine)
print(f"Products: {products['count'][0]:,}")

order_items = pd.read_sql("SELECT COUNT(*) as count FROM raw.order_items", engine)
print(f"Order Items: {order_items['count'][0]:,}")

# Sample data
print("\n📊 Sample Customer Data:")
sample = pd.read_sql("SELECT * FROM raw.customers LIMIT 5", engine)
print(sample)

# Test a complex query
print("\n💰 Top 5 Customers by Revenue:")
top_customers = pd.read_sql("""
    SELECT 
        c.customer_name,
        c.country,
        COUNT(DISTINCT o.order_id) as order_count,
        SUM(o.total_amount) as total_revenue
    FROM raw.customers c
    JOIN raw.orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.customer_name, c.country
    ORDER BY total_revenue DESC
    LIMIT 5
""", engine)
print(top_customers)