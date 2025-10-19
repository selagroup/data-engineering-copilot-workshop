#!/bin/bash

# GitHub Copilot Data Engineering Workshop - Automated Setup Script
# Run this script to set up everything automatically

set -e  # Exit on error

echo "🚀 Starting GitHub Copilot Workshop Setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if command -v python3 &> /dev/null; then
    print_status "Python3 found: $(python3 --version)"
else
    print_error "Python3 not found. Please install Python 3.9+"
    exit 1
fi

# Check Docker
if command -v docker &> /dev/null; then
    print_status "Docker found: $(docker --version)"
else
    print_error "Docker not found. Please install Docker Desktop"
    exit 1
fi

# Check Git
if command -v git &> /dev/null; then
    print_status "Git found: $(git --version)"
else
    print_error "Git not found. Please install Git"
    exit 1
fi

# Create project directory
PROJECT_DIR="copilot-data-engineering-workshop"
if [ -d "$PROJECT_DIR" ]; then
    print_warning "Directory $PROJECT_DIR already exists. Remove it? (y/n)"
    read -r response
    if [ "$response" = "y" ]; then
        rm -rf "$PROJECT_DIR"
    else
        echo "Exiting..."
        exit 0
    fi
fi

mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

print_status "Created project directory: $PROJECT_DIR"

# Initialize git repository
git init
print_status "Initialized Git repository"

# Create directory structure
echo "📁 Creating directory structure..."

directories=(
    "setup/sample_data"
    "notebooks"
    "src/data_pipeline"
    "src/utils"
    "src/templates/sql_templates"
    "dags"
    "tests"
    "exercises/solutions"
    "config"
    ".vscode"
)

for dir in "${directories[@]}"; do
    mkdir -p "$dir"
    touch "$dir/__init__.py" 2>/dev/null || true
done

print_status "Directory structure created"

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Jupyter
.ipynb_checkpoints/
*.ipynb_checkpoints

# IDE
.vscode/
.idea/
*.swp
*.swo

# Data
*.csv
*.parquet
*.db
*.sqlite

# Logs
logs/
*.log

# Environment
.env
.env.local

# Airflow
airflow.db
airflow-webserver.pid
webserver_config.py

# Docker volumes
postgres_data/
minio_data/

# OS
.DS_Store
Thumbs.db
EOF

print_status "Created .gitignore"

# Create requirements.txt
cat > requirements.txt << 'EOF'
# Data Processing
pandas==2.0.3
numpy==1.24.3
pyarrow==12.0.1
openpyxl==3.1.2

# PySpark
pyspark==3.4.1
py4j==0.10.9.7

# Database
psycopg2-binary==2.9.7
sqlalchemy==1.4.48  # Compatible with Airflow 2.7.1
pymongo==4.4.1

# Airflow
apache-airflow==2.7.1
apache-airflow-providers-postgres==5.6.0
apache-airflow-providers-amazon==8.5.1

# SQL & Templates
jinja2==3.1.2
jinjasql==0.1.8

# Testing
pytest==7.4.2
faker==19.6.1
pytest-cov==4.1.0

# Utilities
python-dotenv==1.0.0
rich==13.5.2
tabulate==0.9.0

# Notebook
jupyter==1.0.0
ipykernel==6.25.1
notebook==7.0.3
EOF

print_status "Created requirements.txt"

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: workshop_postgres
    environment:
      POSTGRES_USER: dataeng
      POSTGRES_PASSWORD: copilot123
      POSTGRES_DB: workshop_db
    ports:
      - "5432:5432"
    volumes:
      - ./setup/init_db.sql:/docker-entrypoint-initdb.d/init.sql
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dataeng"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7
    container_name: workshop_redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  minio:
    image: minio/minio
    container_name: workshop_minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

volumes:
  postgres_data:
  minio_data:
EOF

print_status "Created docker-compose.yml"

# Create .env.example
cat > .env.example << 'EOF'
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=workshop_db
DB_USER=dataeng
DB_PASSWORD=copilot123

# MinIO
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Airflow
AIRFLOW_HOME=/opt/airflow
EOF

print_status "Created .env.example"

# Copy .env.example to .env
cp .env.example .env
print_status "Created .env from template"

# Create database initialization script
cat > setup/init_db.sql << 'EOF'
-- Create schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Create sample tables
CREATE TABLE IF NOT EXISTS raw.customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(255),
    email VARCHAR(255),
    country VARCHAR(100),
    signup_date DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES raw.customers(customer_id),
    order_date DATE,
    total_amount DECIMAL(10,2),
    discount_amount DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(50),
    payment_method VARCHAR(50),
    shipping_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(255),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    price DECIMAL(10,2),
    cost DECIMAL(10,2),
    stock_quantity INTEGER,
    supplier_id INTEGER,
    is_discontinued BOOLEAN DEFAULT false
);

CREATE TABLE IF NOT EXISTS raw.order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES raw.orders(order_id),
    product_id INTEGER REFERENCES raw.products(product_id),
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    discount_percent DECIMAL(5,2) DEFAULT 0
);

-- Create indexes for better performance
CREATE INDEX idx_orders_customer_id ON raw.orders(customer_id);
CREATE INDEX idx_orders_date ON raw.orders(order_date);
CREATE INDEX idx_order_items_order_id ON raw.order_items(order_id);
CREATE INDEX idx_order_items_product_id ON raw.order_items(product_id);

-- Create a view for demo purposes
CREATE OR REPLACE VIEW analytics.customer_summary AS
SELECT 
    c.customer_id,
    c.customer_name,
    c.country,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(o.total_amount) as lifetime_value,
    MAX(o.order_date) as last_order_date
FROM raw.customers c
LEFT JOIN raw.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name, c.country;
EOF

print_status "Created database initialization script"

# Create mock data generator
cat > setup/generate_mock_data.py << 'EOF'
"""Generate mock data for the workshop database"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import psycopg2

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
        
        # Order date should be after customer signup
        order_date = fake.date_between(
            start_date=customer['signup_date'], 
            end_date='today'
        )
        
        # Generate order
        order_total = 0
        num_items = random.randint(1, 5)
        discount_amount = 0
        
        for j in range(num_items):
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
        
        # Apply order-level discount
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

def save_to_csv(customers_df, products_df, orders_df, order_items_df):
    """Save dataframes to CSV files"""
    os.makedirs('setup/sample_data', exist_ok=True)
    
    customers_df.to_csv('setup/sample_data/customers.csv', index=False)
    products_df.to_csv('setup/sample_data/products.csv', index=False)
    orders_df.to_csv('setup/sample_data/orders.csv', index=False)
    order_items_df.to_csv('setup/sample_data/order_items.csv', index=False)
    
    # Create a transactions parquet for PySpark demos
    transactions_df = orders_df.merge(
        order_items_df, on='order_id'
    ).merge(
        customers_df[['customer_id', 'customer_name', 'country']], on='customer_id'
    ).merge(
        products_df[['product_id', 'product_name', 'category']], on='product_id'
    )
    
    transactions_df.to_parquet('setup/sample_data/transactions.parquet', index=False)
    
    print("✅ Sample data files created in setup/sample_data/")

def load_to_database(customers_df, products_df, orders_df, order_items_df):
    """Load data to PostgreSQL database"""
    try:
        # Create connection
        engine = create_engine(
            f"postgresql://{os.getenv('DB_USER', 'dataeng')}:"
            f"{os.getenv('DB_PASSWORD', 'copilot123')}@"
            f"{os.getenv('DB_HOST', 'localhost')}:"
            f"{os.getenv('DB_PORT', '5432')}/"
            f"{os.getenv('DB_NAME', 'workshop_db')}"
        )
        
        # Load data to database
        customers_df.to_sql('customers', engine, schema='raw', if_exists='append', index=False)
        products_df.to_sql('products', engine, schema='raw', if_exists='append', index=False)
        orders_df.to_sql('orders', engine, schema='raw', if_exists='append', index=False)
        order_items_df.to_sql('order_items', engine, schema='raw', if_exists='append', index=False)
        
        print("✅ Data loaded to PostgreSQL database")
        
    except Exception as e:
        print(f"⚠️ Could not load to database: {e}")
        print("  Data is still available in CSV files")

if __name__ == "__main__":
    print("🔄 Generating mock data...")
    
    # Generate data
    customers_df = generate_customers(1000)
    products_df = generate_products(200)
    orders_df, order_items_df = generate_orders(customers_df, products_df, 5000)
    
    # Save to files
    save_to_csv(customers_df, products_df, orders_df, order_items_df)
    
    # Try to load to database
    load_to_database(customers_df, products_df, orders_df, order_items_df)
    
    # Print summary
    print("\n📊 Data Generation Summary:")
    print(f"  • Customers: {len(customers_df):,}")
    print(f"  • Products: {len(products_df):,}")
    print(f"  • Orders: {len(orders_df):,}")
    print(f"  • Order Items: {len(order_items_df):,}")
EOF

print_status "Created mock data generator"

# Create Python virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv

# Activate virtual environment and install packages
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1

print_status "Python environment created and packages installed"

# Start Docker containers
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Wait for containers to be healthy
echo "⏳ Waiting for containers to be ready..."
sleep 10

# Check if containers are running
if docker ps | grep -q workshop_postgres; then
    print_status "PostgreSQL container is running"
else
    print_error "PostgreSQL container failed to start"
fi

if docker ps | grep -q workshop_redis; then
    print_status "Redis container is running"
else
    print_error "Redis container failed to start"
fi

if docker ps | grep -q workshop_minio; then
    print_status "MinIO container is running"
else
    print_error "MinIO container failed to start"
fi

# Generate mock data
echo "📊 Generating mock data..."
python setup/generate_mock_data.py

# Create README
cat > README.md << 'EOF'
# GitHub Copilot Workshop - Data Engineering Team

## 🚀 Quick Start

1. **Activate Python environment:**
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Start services:**
   ```bash
   docker-compose up -d
   ```

3. **Open VS Code:**
   ```bash
   code .
   ```

4. **Start Jupyter:**
   ```bash
   jupyter notebook
   ```

## 📁 Project Structure

- `notebooks/` - Jupyter notebooks for demos
- `src/` - Source code for data pipelines
- `dags/` - Airflow DAGs
- `exercises/` - Hands-on exercises
- `setup/sample_data/` - Sample datasets

## 🔗 Service URLs

- PostgreSQL: `localhost:5432`
- MinIO Console: `http://localhost:9001`
- Redis: `localhost:6379`

## 🛠 Tools & Technologies

- Python (pandas, PySpark)
- SQL & Jinja2
- Apache Airflow
- PostgreSQL
- MinIO (S3-compatible storage)

## 📚 Workshop Exercises

1. SQL Query Generation with Copilot
2. Pandas Data Transformations
3. PySpark Pipeline Development
4. Airflow DAG Creation
5. Data Quality Checks

## 💡 Copilot Tips

- Write descriptive comments first
- Use Tab to accept suggestions
- Use Ctrl+Enter to see alternatives
- Keep files with context open in tabs
EOF

print_status "Created README.md"

# Create VS Code settings
cat > .vscode/settings.json << 'EOF'
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "github.copilot.enable": {
        "*": true,
        "yaml": true,
        "plaintext": true,
        "markdown": true,
        "sql": true,
        "jupyter": true
    },
    "editor.inlineSuggest.enabled": true,
    "editor.suggestSelection": "first",
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true
    },
    "editor.rulers": [88],
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black"
}
EOF

print_status "Created VS Code settings"

# Final summary
echo ""
echo "=========================================="
echo -e "${GREEN}✨ Workshop Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "📋 Next Steps:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Test the database connection:"
echo "     python -c \"import pandas as pd; from sqlalchemy import create_engine; engine = create_engine('postgresql://dataeng:copilot123@localhost:5432/workshop_db'); print(pd.read_sql('SELECT COUNT(*) FROM raw.customers', engine))\""
echo ""
echo "  3. Open VS Code:"
echo "     code ."
echo ""
echo "  4. Start Jupyter Notebook:"
echo "     jupyter notebook"
echo ""
echo "🔗 Service URLs:"
echo "  • PostgreSQL: localhost:5432"
echo "  • MinIO Console: http://localhost:9001"
echo "  • Redis: localhost:6379"
echo ""
echo "📚 Documentation: See README.md for detailed instructions"
echo ""
echo "Good luck with your workshop! 🎉"
