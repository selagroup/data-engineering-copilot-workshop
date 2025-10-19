import pandas as pd
import random
import os

print("📦 Creating order_items.csv (simple version)...")

# Make sure directory exists
os.makedirs('setup/sample_data', exist_ok=True)

# Load orders and products to get valid IDs
try:
    orders_df = pd.read_csv('setup/sample_data/orders.csv')
    products_df = pd.read_csv('setup/sample_data/products.csv')
    order_ids = orders_df['order_id'].tolist()
    product_ids = products_df['product_id'].tolist()
    product_prices = dict(zip(products_df['product_id'], products_df['price']))
    print(f"✅ Found {len(order_ids)} orders and {len(product_ids)} products")
except:
    print("⚠️ Could not load orders/products, using defaults...")
    order_ids = list(range(1, 5001))  # Assume 5000 orders
    product_ids = list(range(1, 201))  # Assume 200 products
    product_prices = {i: random.uniform(10, 500) for i in product_ids}

# Generate order items
order_items = []
order_item_id = 1

print(f"Generating items for {len(order_ids)} orders...")

for order_id in order_ids:
    # Each order gets 1-5 items
    num_items = random.randint(1, 5)
    
    for _ in range(num_items):
        product_id = random.choice(product_ids)
        
        order_items.append({
            'order_item_id': order_item_id,
            'order_id': order_id,
            'product_id': product_id,
            'quantity': random.randint(1, 5),
            'unit_price': round(product_prices.get(product_id, random.uniform(10, 500)), 2),
            'discount_percent': random.choice([0, 0, 0, 0, 5, 10, 15])  # Most have no discount
        })
        order_item_id += 1
    
    # Progress indicator
    if len(order_items) % 5000 == 0:
        print(f"  Generated {len(order_items)} items so far...")

# Save to CSV
df = pd.DataFrame(order_items)
df.to_csv('setup/sample_data/order_items.csv', index=False)

print(f"\n✅ Successfully created order_items.csv with {len(df)} records!")
print(f"   Average items per order: {len(df) / len(order_ids):.2f}")

# Display sample
print("\nSample data (first 5 rows):")
print(df.head())

print("\n✨ File saved to: setup/sample_data/order_items.csv")
print("Now run: python simple_load_data.py")