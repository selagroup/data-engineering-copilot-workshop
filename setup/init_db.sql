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
    customer_id INTEGER,
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
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    discount_percent DECIMAL(5,2) DEFAULT 0
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON raw.orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_date ON raw.orders(order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON raw.order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON raw.order_items(product_id);