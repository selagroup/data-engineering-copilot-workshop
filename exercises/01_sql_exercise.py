"""
Exercise 1: Comment to Code
Learn to write comments that generate perfect code with Copilot
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# Database connection
engine = create_engine('postgresql://dataeng:copilot123@localhost:5432/workshop_db')

# EXERCISE 1.1: Basic SQL Generation
# Find the top 10 customers by revenue

# EXERCISE 1.2: Complex Aggregation
# TODO: Generate a query to calculate monthly cohort retention rates

# EXERCISE 1.3: Data Pipeline Function
# TODO: Create a function that:
# - Loads orders data from the database
# - Filters for completed orders only  
# - Calculates daily revenue
# - Identifies anomalies (>2 std dev from mean)
# - Returns a summary DataFrame

# EXERCISE 1.4: Data Quality Checks
# TODO: Generate a comprehensive data quality check function
# Requirements:
# - Check for nulls in required fields
# - Validate email formats
# - Check for duplicate records
# - Verify referential integrity
# - Return detailed report

# EXERCISE 1.5: PySpark Transformation
# TODO: Convert this pandas operation to PySpark:
"""
df.groupby(['customer_id', 'product_category'])
  .agg({
      'order_amount': 'sum',
      'order_id': 'count',
      'order_date': ['min', 'max']
  })
  .reset_index()
"""

# ADVANCED EXERCISE: Complete ETL Pipeline
# TODO: Using only comments, generate a complete ETL pipeline that:
# 1. Extracts data from multiple tables
# 2. Performs complex transformations
# 3. Handles errors gracefully
# 4. Logs progress
# 5. Saves results to both database and parquet