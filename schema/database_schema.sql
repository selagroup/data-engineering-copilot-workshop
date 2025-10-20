-- Database Schema for Workshop
-- Schema: raw

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Customers Table
CREATE TABLE IF NOT EXISTS raw.customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(255),
    email VARCHAR(255),
    country VARCHAR(100),
    signup_date DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products Table
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

-- Orders Table
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

CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON raw.orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_date ON raw.orders(order_date);

-- Order Items Table
CREATE TABLE IF NOT EXISTS raw.order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES raw.orders(order_id),
    product_id INTEGER REFERENCES raw.products(product_id),
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    discount_percent DECIMAL(5,2) DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON raw.order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON raw.order_items(product_id);

-- Foreign Key Constraints (recreated for safety)
ALTER TABLE raw.orders 
    ADD CONSTRAINT IF NOT EXISTS orders_customer_id_fkey 
    FOREIGN KEY (customer_id) REFERENCES raw.customers(customer_id);
ALTER TABLE raw.order_items 
    ADD CONSTRAINT IF NOT EXISTS order_items_order_id_fkey 
    FOREIGN KEY (order_id) REFERENCES raw.orders(order_id);
ALTER TABLE raw.order_items 
    ADD CONSTRAINT IF NOT EXISTS order_items_product_id_fkey 
    FOREIGN KEY (product_id) REFERENCES raw.products(product_id);

-- Analytics Views
CREATE SCHEMA IF NOT EXISTS analytics;

-- Customer Summary View
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
GROUP BY c.customer_id, c.customer_name, c.country;

-- Product Performance View
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

-- Monthly Sales View
CREATE OR REPLACE VIEW analytics.monthly_sales AS
SELECT 
    DATE_TRUNC('month', o.order_date) as month,
    COUNT(DISTINCT o.order_id) as order_count,
    COUNT(DISTINCT o.customer_id) as unique_customers,
    SUM(o.total_amount) as total_revenue,
    AVG(o.total_amount) as avg_order_value
FROM raw.orders o
GROUP BY DATE_TRUNC('month', o.order_date)
ORDER BY month DESC;
