# 🐛 Data Pipeline Debugging Guide

## Overview
This notebook (`demo_debugging.ipynb`) contains a deliberately broken data pipeline designed to demonstrate GitHub Copilot's debugging and code review capabilities. The pipeline processes sales data from a PostgreSQL database using PySpark.

## Learning Objectives
- Use GitHub Copilot to identify bugs through code review
- Apply Copilot suggestions to fix logic errors
- Optimize performance with Copilot's recommendations
- Add error handling and data validation

---

## 🎯 Strategy for Using GitHub Copilot

### Phase 1: Discovery
Ask Copilot to review the code:
- "Review this code for potential issues"
- "What performance problems do you see?"
- "Check this cell for bugs"
- "Explain what this code is trying to do"

### Phase 2: Fix Issues
Use Copilot to generate fixes:
- "Fix the join condition in this cell"
- "Correct the discount calculation"
- "Add null handling to this aggregation"
- "Optimize this data loading"

### Phase 3: Refactor
Improve code quality:
- "Refactor this code for better performance"
- "Add error handling"
- "Extract this logic into a reusable function"
- "Add data validation checks"

---

## 🐛 Issues in the Notebook (Solutions Guide)

### **Step 1: Load Data from Database**

#### Issue #1: Performance - Loading Entire Tables
**Problem:**
- Uses `SELECT *` to load all columns even when only a few are needed
- No predicate pushdown - filtering happens in Spark instead of the database
- Loads all data regardless of date range or status

**Impact:**
- Unnecessary network traffic
- Higher memory usage
- Slower query performance

**Solution:**
```python
# Instead of loading entire tables, use SQL queries to select only needed columns
# and filter at the source

# Example: Load only active customers with specific columns
customers = spark.read \
    .format("jdbc") \
    .option("url", DB_CONNECTION) \
    .option("dbtable", "(SELECT customer_id, customer_name, country FROM raw.customers WHERE is_active = true) AS customers") \
    .option("driver", "org.postgresql.Driver") \
    .load()

# Example: Load only recent orders
orders = spark.read \
    .format("jdbc") \
    .option("url", DB_CONNECTION) \
    .option("dbtable", """(
        SELECT order_id, customer_id, order_date, total_amount, status 
        FROM raw.orders 
        WHERE order_date >= '2023-01-01' 
        AND status IN ('completed', 'shipped')
    ) AS orders""") \
    .option("driver", "org.postgresql.Driver") \
    .load()
```

**Copilot Prompt Suggestions:**
- "Optimize this data loading to only fetch required columns"
- "Add predicate pushdown to filter data at the database level"
- "Rewrite this to load only active customers and recent orders"

---

### **Step 2: Calculate Product Revenue**

#### Issue #2: Wrong Join Key
**Problem:**
```python
product_sales = order_items.join(
    products,
    order_items.order_id == products.product_id,  # WRONG!
    "inner"
)
```
- Joins `order_items.order_id` with `products.product_id`
- Should join on `product_id == product_id`
- This creates incorrect matches and data duplication

**Impact:**
- Completely wrong results
- Data multiplication
- Incorrect revenue calculations

**Solution:**
```python
product_sales = order_items.join(
    products,
    order_items.product_id == products.product_id,  # Correct!
    "inner"
)
```

#### Issue #3: Incorrect Discount Calculation
**Problem:**
```python
F.col("quantity") * F.col("unit_price") * (1 - F.col("discount_percent"))
```
- `discount_percent` in the database is stored as a percentage (e.g., 5.0 means 5%)
- Code treats it as a decimal (e.g., 5.0 would mean 500% discount!)

**Impact:**
- Negative revenue values
- Completely inaccurate financial calculations

**Solution:**
```python
product_sales = product_sales.withColumn(
    "line_total",
    F.col("quantity") * F.col("unit_price") * (1 - F.col("discount_percent") / 100)  # Divide by 100!
)
```

#### Issue #4: Missing Null Handling
**Problem:**
- No validation for null values in `quantity`, `unit_price`, or `discount_percent`
- No handling of discontinued products

**Solution:**
```python
# Add null handling and validation
product_sales = product_sales.withColumn(
    "line_total",
    F.when(
        (F.col("quantity").isNotNull()) & 
        (F.col("unit_price").isNotNull()) & 
        (F.col("quantity") > 0) & 
        (F.col("unit_price") > 0),
        F.col("quantity") * F.col("unit_price") * (1 - F.coalesce(F.col("discount_percent"), F.lit(0)) / 100)
    ).otherwise(0)
)
```

**Copilot Prompt Suggestions:**
- "Fix the join condition between order_items and products"
- "Correct the discount percentage calculation"
- "Add null handling to the revenue calculation"

---

### **Step 3: Customer Segmentation (RFM Analysis)**

#### Issue #5: Hard-coded Reference Date
**Problem:**
```python
reference_date = datetime(2024, 1, 1)  # Static date!
```
- Uses a hard-coded date instead of dynamic calculation
- RFM analysis becomes outdated immediately

**Solution:**
```python
# Option 1: Use current date
reference_date = datetime.now()

# Option 2: Use max order date from the data (more realistic for historical analysis)
max_order_date = orders.agg(F.max("order_date")).collect()[0][0]
reference_date = max_order_date
```

#### Issue #6: Wrong Aggregation Function
**Problem:**
```python
F.count("order_id").alias("frequency")  # Counts all rows, including nulls and duplicates
```
- Should use `countDistinct` to count unique orders

**Solution:**
```python
F.countDistinct("order_id").alias("frequency")
```

#### Issue #7: Reversed RFM Scoring Logic
**Problem:**
```python
F.when(F.col("recency") < 30, 1)  # Lower recency gets lower score - WRONG!
```
- In RFM, lower recency (more recent purchase) should get a HIGHER score
- Current logic is backwards

**Solution:**
```python
rfm = rfm.withColumn(
    "r_score",
    F.when(F.col("recency") < 30, 5)      # Most recent = best score
     .when(F.col("recency") < 60, 4)
     .when(F.col("recency") < 90, 3)
     .when(F.col("recency") < 180, 2)
     .otherwise(1)                         # Least recent = worst score
)
```

#### Issue #8: Missing Null Handling for Customers Without Orders
**Problem:**
```python
F.col("r_score") + F.col("f_score") + F.col("m_score")  # Fails on nulls!
```
- Left join includes customers without orders
- These customers will have null values causing calculation errors

**Solution:**
```python
rfm = rfm.withColumn(
    "rfm_score",
    F.coalesce(F.col("r_score"), F.lit(0)) + 
    F.coalesce(F.col("f_score"), F.lit(0)) + 
    F.coalesce(F.col("m_score"), F.lit(0))
)

# Or filter out customers without orders
rfm = rfm.filter(F.col("frequency").isNotNull() & (F.col("frequency") > 0))
```

**Copilot Prompt Suggestions:**
- "Make the reference date dynamic instead of hard-coded"
- "Fix the RFM recency scoring logic"
- "Add null handling for customers without orders"
- "Use countDistinct for frequency calculation"

---

### **Step 4: Sales Trend Analysis**

#### Issue #9: Date Format Returns String
**Problem:**
```python
F.date_format("order_date", "yyyy-MM")  # Returns string!
```
- `date_format` returns a string, not a date
- String sorting doesn't work correctly for dates ("2023-02" comes before "2023-11" alphabetically)

**Solution:**
```python
# Use date_trunc to keep it as a date type
monthly_sales = orders.withColumn(
    "month",
    F.date_trunc("month", "order_date")
)

# Or cast the string back to date
monthly_sales = orders.withColumn(
    "month",
    F.to_date(F.date_format("order_date", "yyyy-MM-01"))
)
```

#### Issue #10: Wrong Aggregation Functions
**Problem:**
```python
F.sum("order_id").alias("unique_customers")      # WRONG! Sums IDs instead of counting
F.sum("total_amount").alias("avg_order_value")  # WRONG! Should be AVG not SUM
```

**Solution:**
```python
monthly_sales = monthly_sales.groupBy("month") \
    .agg(
        F.count("order_id").alias("total_orders"),
        F.countDistinct("customer_id").alias("unique_customers"),  # Correct!
        F.sum("total_amount").alias("revenue"),
        F.avg("total_amount").alias("avg_order_value")  # Correct!
    )
```

#### Issue #11: No Status Filtering
**Problem:**
- Includes all orders regardless of status
- Should exclude cancelled, returned, or failed orders

**Solution:**
```python
# Filter before aggregation
active_orders = orders.filter(
    F.col("status").isin(['completed', 'shipped', 'delivered'])
)

monthly_sales = active_orders.withColumn(
    "month",
    F.date_trunc("month", "order_date")
)
```

#### Issue #12: Wrong Window Function
**Problem:**
```python
F.lead("revenue").over(windowSpec)  # Gets NEXT month, not previous!
```
- `lead()` looks forward to the next row
- Should use `lag()` to look back to the previous month

**Solution:**
```python
monthly_sales = monthly_sales.withColumn(
    "prev_month_revenue",
    F.lag("revenue").over(windowSpec)  # Correct!
)
```

**Copilot Prompt Suggestions:**
- "Fix the date sorting issue in monthly aggregation"
- "Correct the aggregation functions for unique customers and average order value"
- "Add filtering to exclude cancelled orders"
- "Fix the window function to get previous month instead of next month"

---

## 🎓 Complete Fixed Version

Here's what the corrected code should look like:

### Step 1: Optimized Data Loading
```python
# Load only required columns and apply filters at source
customers = spark.read \
    .format("jdbc") \
    .option("url", DB_CONNECTION) \
    .option("dbtable", "(SELECT customer_id, customer_name, country FROM raw.customers WHERE is_active = true) AS customers") \
    .option("driver", "org.postgresql.Driver") \
    .load()

orders = spark.read \
    .format("jdbc") \
    .option("url", DB_CONNECTION) \
    .option("dbtable", """(
        SELECT order_id, customer_id, order_date, total_amount, status 
        FROM raw.orders 
        WHERE status IN ('completed', 'shipped', 'delivered')
    ) AS orders""") \
    .option("driver", "org.postgresql.Driver") \
    .load()

order_items = spark.read \
    .format("jdbc") \
    .option("url", DB_CONNECTION) \
    .option("dbtable", "(SELECT order_item_id, order_id, product_id, quantity, unit_price, discount_percent FROM raw.order_items) AS order_items") \
    .option("driver", "org.postgresql.Driver") \
    .load()

products = spark.read \
    .format("jdbc") \
    .option("url", DB_CONNECTION) \
    .option("dbtable", "(SELECT product_id, product_name, category, price FROM raw.products WHERE is_discontinued = false) AS products") \
    .option("driver", "org.postgresql.Driver") \
    .load()
```

### Step 2: Fixed Product Revenue
```python
# Correct join and discount calculation
product_sales = order_items.join(
    products,
    order_items.product_id == products.product_id,  # Correct join key!
    "inner"
)

# Fixed discount calculation with null handling
product_sales = product_sales.withColumn(
    "line_total",
    F.col("quantity") * F.col("unit_price") * (1 - F.coalesce(F.col("discount_percent"), F.lit(0)) / 100)
)

revenue_by_product = product_sales.groupBy("product_id", "product_name", "category") \
    .agg(
        F.sum("line_total").alias("total_revenue"),
        F.sum("quantity").alias("total_quantity"),
        F.countDistinct("order_item_id").alias("num_orders")
    )
```

### Step 3: Fixed RFM Analysis
```python
from datetime import datetime

# Dynamic reference date
max_order_date = orders.agg(F.max("order_date")).collect()[0][0]
reference_date = max_order_date

customer_orders = customers.join(
    orders,
    customers.customer_id == orders.customer_id,
    "left"
)

# Fixed aggregation with countDistinct
rfm = customer_orders.groupBy("customer_id", "customer_name", "country") \
    .agg(
        F.datediff(F.lit(reference_date), F.max("order_date")).alias("recency"),
        F.countDistinct("order_id").alias("frequency"),  # Fixed!
        F.sum("total_amount").alias("monetary")
    )

# Corrected RFM scoring - lower recency is better!
rfm = rfm.withColumn(
    "r_score",
    F.when(F.col("recency") < 30, 5)      # Fixed!
     .when(F.col("recency") < 60, 4)
     .when(F.col("recency") < 90, 3)
     .when(F.col("recency") < 180, 2)
     .otherwise(1)
).withColumn(
    "f_score",
    F.when(F.col("frequency") >= 10, 5)
     .when(F.col("frequency") >= 5, 4)
     .when(F.col("frequency") >= 3, 3)
     .when(F.col("frequency") >= 2, 2)
     .otherwise(1)
).withColumn(
    "m_score",
    F.when(F.col("monetary") >= 10000, 5)
     .when(F.col("monetary") >= 5000, 4)
     .when(F.col("monetary") >= 2000, 3)
     .when(F.col("monetary") >= 1000, 2)
     .otherwise(1)
)

# Fixed null handling
rfm = rfm.withColumn(
    "rfm_score",
    F.coalesce(F.col("r_score"), F.lit(0)) + 
    F.coalesce(F.col("f_score"), F.lit(0)) + 
    F.coalesce(F.col("m_score"), F.lit(0))
)
```

### Step 4: Fixed Sales Trends
```python
# Fixed date handling and aggregations
monthly_sales = orders.withColumn(
    "month",
    F.date_trunc("month", "order_date")  # Returns date type!
)

monthly_sales = monthly_sales.groupBy("month") \
    .agg(
        F.count("order_id").alias("total_orders"),
        F.countDistinct("customer_id").alias("unique_customers"),  # Fixed!
        F.sum("total_amount").alias("revenue"),
        F.avg("total_amount").alias("avg_order_value")  # Fixed!
    )

print("Monthly Sales Trends:")
monthly_sales.orderBy("month").show(12)  # Now sorts correctly!

# Fixed window function
windowSpec = Window.orderBy("month")
monthly_sales = monthly_sales.withColumn(
    "prev_month_revenue",
    F.lag("revenue").over(windowSpec)  # Fixed!
)

monthly_sales = monthly_sales.withColumn(
    "growth_rate",
    F.when(F.col("prev_month_revenue").isNotNull(),
        ((F.col("revenue") - F.col("prev_month_revenue")) / F.col("prev_month_revenue") * 100)
    ).otherwise(None)
)
```

---

## 📊 Summary of All Issues

| # | Category | Issue | Severity | Impact |
|---|----------|-------|----------|--------|
| 1 | Performance | Loading entire tables with SELECT * | Medium | Slow, wasteful |
| 2 | Logic Error | Wrong join key (order_id vs product_id) | Critical | Wrong results |
| 3 | Logic Error | Incorrect discount calculation | Critical | Wrong revenue |
| 4 | Data Quality | Missing null handling | High | Runtime errors |
| 5 | Code Quality | Hard-coded reference date | Medium | Outdated analysis |
| 6 | Logic Error | count() instead of countDistinct() | High | Inflated frequency |
| 7 | Logic Error | Reversed RFM recency scoring | High | Wrong segments |
| 8 | Data Quality | No null handling for customers without orders | High | Calculation errors |
| 9 | Logic Error | Date format returns string | Medium | Wrong sorting |
| 10 | Logic Error | SUM instead of countDistinct for customers | Critical | Wrong metrics |
| 11 | Logic Error | SUM instead of AVG for order value | Critical | Wrong metrics |
| 12 | Data Quality | No status filtering | Medium | Includes bad orders |
| 13 | Logic Error | lead() instead of lag() for previous month | High | Wrong growth rate |

---

## 🚀 Extension Exercises

Once you've fixed all the bugs, try these challenges:

1. **Add Data Quality Checks**: Use Copilot to add validation for negative values, outliers, etc.
2. **Create Reusable Functions**: Extract common patterns into functions
3. **Add Error Handling**: Wrap operations in try/catch blocks
4. **Add Logging**: Use Copilot to add informative logging
5. **Create Unit Tests**: Generate test cases for each transformation
6. **Add Documentation**: Generate docstrings and comments
7. **Performance Tuning**: Add caching, partitioning, and broadcast joins where appropriate

---

## 💡 Tips for Learning

- Don't look at the solutions first! Try to find issues yourself with Copilot's help
- Compare your fixes with the solutions provided
- Ask Copilot "Why is this wrong?" to understand the issues
- Experiment with different prompts to see what works best
- Try to fix issues in multiple ways and compare approaches
