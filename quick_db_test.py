import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgressadmin:wf**F!$3dGdf14@copilot-workshop-db.postgres.database.azure.com:5432/workshop_db')

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
    print("\n[OK] Database connection successful!")
    
except Exception as e:
    print(f"[ERROR] {e}")
    print("Make sure Docker is running: docker-compose up -d")
