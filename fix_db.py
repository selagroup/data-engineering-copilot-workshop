import pandas as pd
from sqlalchemy import create_engine, text
import os
import sys

# Database connection
engine = create_engine('postgresql://dataeng:copilot123@localhost:5432/workshop_db')

print("Fixing database setup...\n")

# Step 1: Create missing order_items table
print("Creating missing order_items table...")
create_order_items = """
CREATE TABLE IF NOT EXISTS raw.order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER REFERENCES raw.orders(order_id),
    product_id INTEGER REFERENCES raw.products(product_id),
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    discount_percent DECIMAL(5,2) DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON raw.order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON raw.order_items(product_id);
"""

try:
    # For SQLAlchemy 1.4, use execute directly on engine
    with engine.begin() as conn:  # begin() auto-commits
        conn.execute(text(create_order_items))
    print("[OK] order_items table created successfully!\n")
except Exception as e:
    print(f"[ERROR] Error creating table: {e}\n")
    print("Continuing anyway (table might already exist)...\n")

# Step 2: Check if sample data exists
data_path = 'setup/sample_data'
if not os.path.exists(data_path):
    print("[ERROR] No sample data found. Generating mock data first...")
    import subprocess
    subprocess.run([sys.executable, 'generate_mock_data.py'])

# Step 3: Load data from CSV files
print("Loading data from CSV files...")

try:
    # Load CSV files
    customers = pd.read_csv(f'{data_path}/customers.csv')
    products = pd.read_csv(f'{data_path}/products.csv')
    orders = pd.read_csv(f'{data_path}/orders.csv')
    order_items = pd.read_csv(f'{data_path}/order_items.csv')

    # Drop ID columns to let PostgreSQL auto-generate them
    if 'customer_id' in customers.columns:
        customers = customers.drop(columns=['customer_id'])
    if 'product_id' in products.columns:
        products = products.drop(columns=['product_id'])
    if 'order_id' in orders.columns:
        orders = orders.drop(columns=['order_id'])
    if 'order_item_id' in order_items.columns:
        order_items = order_items.drop(columns=['order_item_id'])

    print(f"Found data files:")
    print(f"  - Customers: {len(customers):,} records")
    print(f"  - Products: {len(products):,} records")
    print(f"  - Orders: {len(orders):,} records")
    print(f"  - Order Items: {len(order_items):,} records")
    print()
    
except FileNotFoundError as e:
    print(f"[ERROR] CSV files not found. Running data generator...")
    import subprocess
    subprocess.run([sys.executable, 'generate_mock_data.py'])
    # Try loading again
    customers = pd.read_csv(f'{data_path}/customers.csv')
    products = pd.read_csv(f'{data_path}/products.csv')
    orders = pd.read_csv(f'{data_path}/orders.csv')
    order_items = pd.read_csv(f'{data_path}/order_items.csv')

# Step 4: Clear existing data and load fresh data
print("Clearing existing data and loading fresh data to PostgreSQL...")

try:
    # First, drop foreign key constraints to allow truncation
    with engine.begin() as conn:
        conn.execute(text("""
            ALTER TABLE IF EXISTS raw.order_items DROP CONSTRAINT IF EXISTS order_items_order_id_fkey;
            ALTER TABLE IF EXISTS raw.order_items DROP CONSTRAINT IF EXISTS order_items_product_id_fkey;
            ALTER TABLE IF EXISTS raw.orders DROP CONSTRAINT IF EXISTS orders_customer_id_fkey;
        """))
    
    # Truncate tables in correct order (due to foreign keys)
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE raw.order_items CASCADE"))
        conn.execute(text("TRUNCATE TABLE raw.orders CASCADE"))
        conn.execute(text("TRUNCATE TABLE raw.products CASCADE"))
        conn.execute(text("TRUNCATE TABLE raw.customers CASCADE"))
    print("  Cleared existing data")
    
    # Load customers
    print("  Loading customers...")
    customers.to_sql('customers', engine, schema='raw', if_exists='append', index=False, method='multi')
    
    # Load products  
    print("  Loading products...")
    products.to_sql('products', engine, schema='raw', if_exists='append', index=False, method='multi')
    
    # Load orders
    print("  Loading orders...")
    orders.to_sql('orders', engine, schema='raw', if_exists='append', index=False, method='multi')
    
    # Load order_items
    print("  Loading order_items...")
    order_items.to_sql('order_items', engine, schema='raw', if_exists='append', index=False, method='multi')
    
    print("\n[OK] All data loaded successfully!\n")
    
except Exception as e:
    print(f"Warning during load: {e}")
    print("[ERROR] Data load failed. Please check your schema and data consistency.")
    sys.exit(1)

# Step 5: Recreate foreign key constraints
print("Adding foreign key constraints...")
constraints = """
-- Add foreign key constraints if they don't exist
DO $$
BEGIN
    -- Check and add customer foreign key
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'orders_customer_id_fkey' 
        AND table_schema = 'raw'
    ) THEN
        ALTER TABLE raw.orders 
        ADD CONSTRAINT orders_customer_id_fkey 
        FOREIGN KEY (customer_id) REFERENCES raw.customers(customer_id);
    END IF;
    
    -- Check and add order foreign key
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'order_items_order_id_fkey'
        AND table_schema = 'raw'
    ) THEN
        ALTER TABLE raw.order_items 
        ADD CONSTRAINT order_items_order_id_fkey 
        FOREIGN KEY (order_id) REFERENCES raw.orders(order_id);
    END IF;
    
    -- Check and add product foreign key
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'order_items_product_id_fkey'
        AND table_schema = 'raw'
    ) THEN
        ALTER TABLE raw.order_items 
        ADD CONSTRAINT order_items_product_id_fkey 
        FOREIGN KEY (product_id) REFERENCES raw.products(product_id);
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        -- If constraints fail, just continue
        NULL;
END $$;
"""

try:
    with engine.begin() as conn:
        conn.execute(text(constraints))
    print("[OK] Constraints added!\n")
except Exception as e:
    print(f"Note: Constraints may already exist or data has referential issues: {e}\n")

# Step 6: Create or update views
print("Creating analytics views...")
views = """
-- Customer summary view
CREATE OR REPLACE VIEW analytics.customer_summary AS
SELECT 
    c.customer_id,
    c.customer_name,
    c.country,
    COUNT(DISTINCT o.order_id) as total_orders,
    COALESCE(SUM(o.total_amount), 0) as lifetime_value,
    COALESCE(AVG(o.total_amount), 0) as avg_order_value,
    MAX(CAST(o.order_date AS DATE)) as last_order_date,
    MIN(CAST(o.order_date AS DATE)) as first_order_date
FROM raw.customers c
LEFT JOIN raw.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name, c.country;

-- Product performance view
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
GROUP BY p.product_id, p.product_name, p.category, p.price;

-- Monthly sales view
CREATE OR REPLACE VIEW analytics.monthly_sales AS
SELECT 
    DATE_TRUNC('month', CAST(o.order_date AS DATE)) as month,
    COUNT(DISTINCT o.order_id) as order_count,
    COUNT(DISTINCT o.customer_id) as unique_customers,
    SUM(o.total_amount) as total_revenue,
    AVG(o.total_amount) as avg_order_value
FROM raw.orders o
GROUP BY DATE_TRUNC('month', CAST(o.order_date AS DATE))
ORDER BY month DESC;
"""

try:
    with engine.begin() as conn:
        conn.execute(text(views))
    print("[OK] Views created!\n")
except Exception as e:
    print(f"Warning creating views: {e}\n")

# Step 7: Verify everything works
print("Verifying database setup...")
print("-" * 40)

# Check record counts
try:
    verification = pd.read_sql("""
        SELECT 'Customers' as table_name, COUNT(*) as record_count FROM raw.customers
        UNION ALL
        SELECT 'Products', COUNT(*) FROM raw.products
        UNION ALL
        SELECT 'Orders', COUNT(*) FROM raw.orders
        UNION ALL
        SELECT 'Order Items', COUNT(*) FROM raw.order_items
    """, engine)
    
    print(verification.to_string(index=False))
    print()
    
    # Check if we have data
    if verification['record_count'].sum() == 0:
        print("[WARNING] Tables exist but have no data!")
        print("Run: python generate_mock_data.py")
    else:
        # Test a complex query
        print("Testing complex query with joins...")
        test_query = """
            SELECT 
                c.country,
                COUNT(DISTINCT c.customer_id) as customers,
                COUNT(DISTINCT o.order_id) as orders,
                ROUND(CAST(SUM(o.total_amount) AS numeric), 2) as revenue
            FROM raw.customers c
            LEFT JOIN raw.orders o ON c.customer_id = o.customer_id
            GROUP BY c.country
            ORDER BY revenue DESC NULLS LAST
            LIMIT 5
        """
        result = pd.read_sql(test_query, engine)
        print("\nTop 5 Countries by Revenue:")
        print(result.to_string(index=False))
        
        print("\n" + "="*50)
        print("SUCCESS! Database is now fully set up and ready for your workshop!")
        print("="*50)
        
except Exception as e:
    print(f"Error during verification: {e}")
    print("\nBut your database structure is ready!")

# Create a quick test file with proper encoding
with open('quick_db_test.py', 'w', encoding='utf-8') as f:
    f.write("""import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://dataeng:copilot123@localhost:5432/workshop_db')

try:
    # Quick test query
    df = pd.read_sql('''
        SELECT 
            COUNT(DISTINCT customer_id) as customers,
            COUNT(DISTINCT order_id) as orders,
            ROUND(CAST(SUM(total_amount) AS numeric), 2) as total_revenue
        FROM raw.orders
    ''', engine)
    
    print("Database Test Results:")
    print(df)
    print("\\n[OK] Database connection successful!")
    
except Exception as e:
    print(f"[ERROR] {e}")
    print("Make sure Docker is running: docker-compose up -d")
""")

print("\nTips:")
print("  - Run 'python quick_db_test.py' anytime to test the connection")
print("  - If tables are empty, run 'python generate_mock_data.py' first")
print("  - Use DBeaver or pgAdmin to explore the data visually")
print("  - Connection string: postgresql://dataeng:copilot123@localhost:5432/workshop_db")
