"""
Exercise 1: Comment to Code - Azure Compatible Version
Learn to write comments that generate perfect code with Copilot
Works with both local Docker PostgreSQL and Azure PostgreSQL
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

# SCHEMA = {
#     "raw.customers": [
#         "customer_id", "customer_name", "email", "country", "created_at"
#     ],
#     "raw.products": [
#         "product_id", "product_name", "category", "price", "stock_quantity"
#     ],
#     "raw.orders": [
#         "order_id", "customer_id", "order_date", "total_amount", "discount_amount", "status", "payment_method", "shipping_address", "created_at"
#     ],
#     "raw.order_items": [
#         "order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount_percent"
#     ],
#     "analytics.customer_summary": [
#         "customer_id", "customer_name", "country", "total_orders", "lifetime_value", "avg_order_value", "last_order_date", "first_order_date"
#     ],
#     "analytics.product_performance": [
#         "product_id", "product_name", "category", "price", "times_ordered", "total_quantity_sold", "total_revenue"
#     ],
#     "analytics.monthly_sales": [
#         "month", "order_count", "unique_customers", "total_revenue", "avg_order_value"
#     ]
# }

# Database connection - Use environment variable or default to local
db_connection = os.getenv('DB_CONNECTION_STRING', 
                          'postgresql://postgressadmin:wf**F!$3dGdf14@copilot-workshop-db.postgres.database.azure.com:5432/workshop_db')

print(f"🔗 Connecting to database...")
engine = create_engine(db_connection)

try:
    with engine.connect():
        print("✅ Connection successful!\n")
except Exception as e:
    exit(1)

# EXERCISE 1.1: Basic SQL Generation Using only comments
# TODO: Find the top 10 customers by revenue

# sql_query_1_1 = """
# SELECT c.customer_id, c.customer_name, SUM(o.total_amount) AS total_revenue
# FROM raw.customers c
# JOIN raw.orders o ON c.customer_id = o.customer_id
# WHERE o.status = 'delivered'
# GROUP BY c.customer_id, c.customer_name
# HAVING SUM(o.total_amount) > 0
# ORDER BY total_revenue DESC
# LIMIT 10;
# """
# top_customers_df = pd.read_sql(sql_query_1_1, engine)
# print("Top 10 Customers by Revenue:")
# print(top_customers_df)


# EXERCISE 1.2: Complex Aggregation
# TODO: Generate a query to calculate monthly cohort retention rates
sql_query_1_2 = """
WITH first_orders AS (
    SELECT customer_id, MIN(DATE_TRUNC('month', order_date)) AS first_order_month
    FROM raw.orders
    GROUP BY customer_id
), monthly_orders AS (
    SELECT customer_id, DATE_TRUNC('month', order_date) AS order_month
    FROM raw.orders
)
SELECT
    fo.first_order_month,
    mo.order_month,
    COUNT(DISTINCT mo.customer_id) AS retained_customers
FROM first_orders fo
JOIN monthly_orders mo ON fo.customer_id = mo.customer_id
WHERE mo.order_month >= fo.first_order_month
GROUP BY fo.first_order_month, mo.order_month
ORDER BY fo.first_order_month, mo.order_month
"""

cohort_retention_df = pd.read_sql(sql_query_1_2, engine)
print("\nMonthly Cohort Retention Rates:")

print(cohort_retention_df)

# - Loads orders data from the database
# - Filters for completed orders only  
# - Calculates daily revenue
# - Identifies anomalies (>2 std dev from mean)
# - Returns a summary DataFrame




