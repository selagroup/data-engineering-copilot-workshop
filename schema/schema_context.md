# Compact schema context for the workshop database
# Generated from schema/database_schema.sql
SCHEMA = {
    "raw.customers": [
        "customer_id", "customer_name", "email", "country", "created_at"
    ],
    "raw.products": [
        "product_id", "product_name", "category", "price", "stock_quantity"
    ],
    "raw.orders": [
        "order_id", "customer_id", "order_date", "total_amount", "discount_amount", "status", "payment_method", "shipping_address", "created_at"
    ],
    "raw.order_items": [
        "order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount_percent"
    ],
    "analytics.customer_summary": [
        "customer_id", "customer_name", "country", "total_orders", "lifetime_value", "avg_order_value", "last_order_date", "first_order_date"
    ],
    "analytics.product_performance": [
        "product_id", "product_name", "category", "price", "times_ordered", "total_quantity_sold", "total_revenue"
    ],
    "analytics.monthly_sales": [
        "month", "order_count", "unique_customers", "total_revenue", "avg_order_value"
    ]
}
