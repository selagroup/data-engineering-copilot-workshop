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



# EXERCISE 1.2: Complex Aggregation
# TODO: Generate a query to calculate monthly cohort retention rates



# EXERCISE 1.3: Data Pipeline Function
# TODO: Create a function that:
# - Loads orders data from the database
# - Filters for completed orders only  
# - Calculates daily revenue
# - Identifies anomalies (>2 std dev from mean)
# - Returns a summary DataFrame




