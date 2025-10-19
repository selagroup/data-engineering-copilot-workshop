-- Create schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Create sample tables
CREATE TABLE raw.customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(255),
    email VARCHAR(255),
    country VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE raw.orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES raw.customers(customer_id),
    order_date DATE,
    total_amount DECIMAL(10,2),
    status VARCHAR(50)
);

CREATE TABLE raw.products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(255),
    category VARCHAR(100),
    price DECIMAL(10,2),
    stock_quantity INTEGER
);

-- Create indexes
CREATE INDEX idx_orders_customer_id ON raw.orders(customer_id);
CREATE INDEX idx_orders_date ON raw.orders(order_date);