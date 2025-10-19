from sqlalchemy import create_engine, text

engine = create_engine('postgresql://dataeng:copilot123@localhost:5432/workshop_db')

views_sql = '''
-- Customer summary view
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
    DATE_TRUNC('month', o.order_date) as month,
    COUNT(DISTINCT o.order_id) as order_count,
    COUNT(DISTINCT o.customer_id) as unique_customers,
    SUM(o.total_amount) as total_revenue,
    AVG(o.total_amount) as avg_order_value
FROM raw.orders o
GROUP BY DATE_TRUNC('month', o.order_date)
ORDER BY month DESC;
'''

if __name__ == "__main__":
    with engine.begin() as conn:
        for stmt in views_sql.split(';\n'):
            if stmt.strip():
                conn.execute(text(stmt))
    print("[OK] Analytics views created!")
