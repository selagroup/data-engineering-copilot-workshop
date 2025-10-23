# 🐛 Advanced Data Pipeline Debugging Guide

## Overview
This notebook (`broken_data_pipeline.ipynb`) contains a more complex and broken data pipeline for an e-commerce analytics platform. It includes advanced analytics like cohort analysis, product affinity analysis, and customer lifetime value calculation. The pipeline has multiple subtle bugs, performance issues, and data quality problems.

## Learning Objectives
- Debug complex multi-step data transformations
- Identify subtle logic errors in analytical calculations
- Fix window function and aggregation issues
- Optimize join strategies and data loading
- Handle edge cases and null values properly
- Implement data quality checks

---

## 🎯 Strategy for Using GitHub Copilot

### Phase 1: Understanding & Discovery
Ask Copilot to help you understand the pipeline:
- "Explain what this cohort analysis is trying to calculate"
- "Review this code for bugs and performance issues"
- "What could go wrong with this join operation?"
- "Analyze this window function logic"

### Phase 2: Deep Debugging
Use Copilot to identify specific issues:
- "Is this join key correct?"
- "Check if this aggregation handles nulls properly"
- "Review this date calculation for edge cases"
- "Identify performance bottlenecks in this code"

### Phase 3: Fix & Optimize
Generate fixes and improvements:
- "Fix the cohort retention calculation"
- "Optimize this self-join operation"
- "Add proper null handling and data validation"
- "Refactor this for better performance"

### Phase 4: Enhance
Add robustness:
- "Add error handling for edge cases"
- "Create data quality checks"
- "Add logging and monitoring"
- "Write unit tests for this transformation"

---

## 🐛 Issues in the Notebook (Solutions Guide)

### **Step 1: Load Data from Database**

#### Issue #1: Inefficient Data Loading - No Predicate Pushdown
**Problem:**
- Loads entire tables without filtering at the source
- No column pruning - fetches all columns even when only a few are needed
- Missing partitioning configuration for large tables
- No caching strategy for repeatedly used DataFrames

**Impact:**
- Excessive memory usage
- Slow initial load times
- Network bottleneck
- Repeated full table scans

**Solution:**
```python
# Load only required columns and apply source-level filters
customers = spark.read \
    .format("jdbc") \
    .option("url", jdbc_url) \
    .option("dbtable", """(
        SELECT customer_id, customer_name, country, email, join_date 
        FROM raw.customers 
        WHERE is_active = true
    ) AS customers""") \
    .option("user", username) \
    .option("password", password) \
    .option("driver", "org.postgresql.Driver") \
    .load()

# Load orders with date filtering and status filtering
orders = spark.read \
    .format("jdbc") \
    .option("url", jdbc_url) \
    .option("dbtable", """(
        SELECT order_id, customer_id, order_date, total_amount, status 
        FROM raw.orders 
        WHERE order_date >= '2023-01-01'
        AND status IN ('completed', 'shipped', 'delivered')
    ) AS orders""") \
    .option("user", username) \
    .option("password", password) \
    .option("driver", "org.postgresql.Driver") \
    .option("partitionColumn", "order_id") \
    .option("lowerBound", "1") \
    .option("upperBound", "100000") \
    .option("numPartitions", "4") \
    .load()

# Cache frequently used DataFrames
orders.cache()
customers.cache()
```

**Copilot Prompt Suggestions:**
- "Optimize data loading with predicate pushdown"
- "Add partitioning configuration for large table loads"
- "Which DataFrames should be cached in this pipeline?"

---

### **Step 2: Customer Cohort Analysis**

#### Issue #2: Wrong Cohort Assignment Logic
**Problem:**
```python
# Uses order_date instead of customer's first order date for cohort
cohort_data = orders.withColumn(
    "cohort_month",
    F.date_trunc("month", F.col("order_date"))  # WRONG!
)
```
- Assigns customer to multiple cohorts based on each order date
- Should use the customer's FIRST order date as their cohort
- This completely breaks cohort analysis

**Impact:**
- Customers counted in multiple cohorts
- Retention rates are meaningless
- Cohort comparison is invalid

**Solution:**
```python
# Find first order date for each customer
first_orders = orders.groupBy("customer_id").agg(
    F.min("order_date").alias("first_order_date")
)

# Assign cohort based on first order month
cohort_data = orders.join(
    first_orders,
    "customer_id",
    "left"
).withColumn(
    "cohort_month",
    F.date_trunc("month", F.col("first_order_date"))  # Correct!
).withColumn(
    "order_month",
    F.date_trunc("month", F.col("order_date"))
)
```

#### Issue #3: Incorrect Period Calculation
**Problem:**
```python
F.months_between(F.col("order_date"), F.col("cohort_month")).cast("int")
```
- Uses `order_date` instead of `order_month` for period calculation
- This gives incorrect granularity (day-level vs month-level)
- Period numbers won't align properly to months

**Solution:**
```python
cohort_data = cohort_data.withColumn(
    "period_number",
    F.months_between(F.col("order_month"), F.col("cohort_month")).cast("int")
)
```

#### Issue #4: Wrong Aggregation in Retention Calculation
**Problem:**
```python
cohort_counts = cohort_data.groupBy("cohort_month", "period_number").agg(
    F.count("order_id").alias("customers")  # WRONG! Counts orders not customers
)
```
- Counts total orders instead of unique customers
- Multiple orders from same customer in a period inflates retention

**Solution:**
```python
cohort_counts = cohort_data.groupBy("cohort_month", "period_number").agg(
    F.countDistinct("customer_id").alias("customers")  # Correct!
)
```

#### Issue #5: Division by Zero and Null Handling
**Problem:**
```python
F.col("customers") / F.col("cohort_size") * 100
```
- No null checking for cohorts with no period 0 data
- Division by zero when cohort_size is 0
- Missing handling for cohorts with incomplete data

**Solution:**
```python
cohort_retention = cohort_retention.withColumn(
    "retention_rate",
    F.when(
        (F.col("cohort_size").isNotNull()) & (F.col("cohort_size") > 0),
        (F.col("customers") / F.col("cohort_size") * 100).cast("decimal(10,2)")
    ).otherwise(None)
)
```

**Copilot Prompt Suggestions:**
- "Fix the cohort assignment logic to use first order date"
- "Correct the period calculation for monthly cohorts"
- "Add null handling to retention rate calculation"

---

### **Step 3: Product Affinity Analysis (Market Basket)**

#### Issue #6: Self-Join Creates Duplicate Pairs
**Problem:**
```python
product_pairs = order_products.alias("a").join(
    order_products.alias("b"),
    F.col("a.order_id") == F.col("b.order_id"),
    "inner"
)
```
- Self-join without exclusion creates pairs like (A, A)
- Creates duplicate pairs: both (A, B) and (B, A)
- Massively inflates the dataset

**Impact:**
- Wrong affinity scores
- Unnecessary computation
- Memory issues

**Solution:**
```python
product_pairs = order_products.alias("a").join(
    order_products.alias("b"),
    (F.col("a.order_id") == F.col("b.order_id")) & 
    (F.col("a.product_id") < F.col("b.product_id")),  # Prevent duplicates and self-pairs
    "inner"
)
```

#### Issue #7: Wrong Confidence Calculation
**Problem:**
```python
F.col("pair_count") / F.col("product_a_count")  # Simple division, missing context
```
- Doesn't account for minimum support threshold
- No statistical validation
- Missing normalization

**Solution:**
```python
# Calculate support, confidence, and lift properly
affinity_metrics = affinity_metrics.withColumn(
    "support",
    F.col("pair_count") / total_orders  # Proportion of all orders
).withColumn(
    "confidence",
    F.col("pair_count") / F.col("product_a_count")  # P(B|A)
).withColumn(
    "lift",
    F.col("pair_count") / (F.col("product_a_count") * F.col("product_b_count") / total_orders)
).filter(
    (F.col("pair_count") >= 5) &  # Minimum support
    (F.col("confidence") >= 0.01)  # Minimum confidence
)
```

#### Issue #8: Missing Broadcast Join Optimization
**Problem:**
- Self-join on large table without optimization
- Product dimension table not broadcasted
- Results in shuffle-heavy operation

**Solution:**
```python
from pyspark.sql.functions import broadcast

# Broadcast smaller product table
product_pairs = order_products.alias("a").join(
    broadcast(order_products.alias("b")),
    (F.col("a.order_id") == F.col("b.order_id")) & 
    (F.col("a.product_id") < F.col("b.product_id")),
    "inner"
)
```

**Copilot Prompt Suggestions:**
- "Fix the self-join to avoid duplicate product pairs"
- "Add proper market basket analysis metrics"
- "Optimize this self-join with broadcast"

---

### **Step 4: Customer Lifetime Value (CLV)**

#### Issue #9: Incorrect Revenue Attribution
**Problem:**
```python
customer_revenue = orders.groupBy("customer_id").agg(
    F.sum("total_amount").alias("total_revenue")
)
```
- Includes cancelled and returned orders
- No filtering by order status
- Doesn't account for refunds

**Solution:**
```python
# Filter valid orders first
valid_orders = orders.filter(
    F.col("status").isin(['completed', 'shipped', 'delivered'])
)

customer_revenue = valid_orders.groupBy("customer_id").agg(
    F.sum("total_amount").alias("total_revenue"),
    F.count("order_id").alias("order_count"),
    F.avg("total_amount").alias("avg_order_value")
)
```

#### Issue #10: Wrong Customer Lifespan Calculation
**Problem:**
```python
F.datediff(F.current_date(), F.min("order_date")) / 365
```
- Divides by 365 using integer division in some Spark versions
- Should use customer join date, not first order date
- Doesn't handle customers who haven't ordered yet

**Solution:**
```python
# Join with customer data to get join_date
customer_tenure = customers.join(
    valid_orders,
    "customer_id",
    "left"
).groupBy("customer_id", "join_date").agg(
    F.min("order_date").alias("first_order_date"),
    F.max("order_date").alias("last_order_date")
).withColumn(
    "customer_lifespan_years",
    F.when(
        F.col("first_order_date").isNotNull(),
        F.datediff(F.col("last_order_date"), F.col("first_order_date")) / 365.25
    ).otherwise(
        F.datediff(F.current_date(), F.col("join_date")) / 365.25
    )
)
```

#### Issue #11: CLV Formula Doesn't Handle Edge Cases
**Problem:**
```python
F.col("avg_order_value") * F.col("purchase_frequency") * F.col("customer_lifespan_years")
```
- Lifespan of 0 for new customers gives CLV of 0
- Doesn't project future value
- Missing churn rate consideration

**Solution:**
```python
# More robust CLV with minimum lifespan and future projection
clv = clv.withColumn(
    "customer_lifespan_years",
    F.when(F.col("customer_lifespan_years") < 0.5, 0.5)
     .otherwise(F.col("customer_lifespan_years"))
).withColumn(
    "historic_clv",
    F.col("total_revenue")
).withColumn(
    "projected_annual_value",
    F.col("avg_order_value") * F.col("purchase_frequency") * 12
).withColumn(
    "predicted_clv",
    F.col("historic_clv") + (F.col("projected_annual_value") * 2)  # 2-year projection
)
```

#### Issue #12: Missing Join Results in Data Loss
**Problem:**
```python
clv = customer_revenue.join(customer_metrics, "customer_id", "inner")
```
- Inner join loses customers without completed orders
- Should use outer join to keep all customers
- Missing customers get excluded from CLV analysis

**Solution:**
```python
clv = customers.join(
    customer_revenue,
    "customer_id",
    "left"
).join(
    customer_metrics,
    "customer_id",
    "left"
).fillna(0, subset=["total_revenue", "order_count", "avg_order_value"])
```

**Copilot Prompt Suggestions:**
- "Fix the revenue aggregation to exclude invalid orders"
- "Correct the customer lifespan calculation"
- "Improve CLV formula to handle edge cases"
- "Use left join to avoid losing customers"

---

### **Step 5: Sales Performance Dashboard**

#### Issue #13: Incorrect Moving Average Window
**Problem:**
```python
windowSpec = Window.orderBy("order_date").rowsBetween(-6, 0)
```
- `rowsBetween(-6, 0)` gives 7 days, not 7-day rolling average
- Should use `rangeBetween` for time-based windows
- Doesn't handle gaps in dates

**Solution:**
```python
# Use range-based window for proper time-based rolling average
windowSpec = Window.orderBy(F.col("order_date").cast("long")) \
    .rangeBetween(-6 * 86400, 0)  # 6 days in seconds

# Or use rows but ensure daily continuity first
date_range = orders.select(
    F.explode(
        F.sequence(
            F.min("order_date"),
            F.max("order_date"),
            F.expr("INTERVAL 1 DAY")
        )
    ).alias("order_date")
)

daily_sales = date_range.join(
    daily_sales,
    "order_date",
    "left"
).fillna(0, subset=["total_revenue"])
```

#### Issue #14: Cumulative Sum Resets Incorrectly
**Problem:**
```python
windowSpec = Window.orderBy("order_date")  # Missing partitionBy for year
```
- Cumulative sum continues across years
- Should reset at the start of each year for YTD metrics
- Ranks and running totals become meaningless across boundaries

**Solution:**
```python
# Add year partitioning for YTD calculations
daily_sales = daily_sales.withColumn("year", F.year("order_date"))

windowSpec = Window.partitionBy("year").orderBy("order_date") \
    .rowsBetween(Window.unboundedPreceding, 0)

daily_sales = daily_sales.withColumn(
    "ytd_revenue",
    F.sum("total_revenue").over(windowSpec)
)
```

#### Issue #15: Performance Issue - Multiple Aggregations
**Problem:**
```python
# Separate aggregations for each metric
daily_revenue = orders.groupBy("order_date").agg(F.sum("total_amount"))
daily_orders = orders.groupBy("order_date").agg(F.count("order_id"))
daily_customers = orders.groupBy("order_date").agg(F.countDistinct("customer_id"))
```
- Three separate full scans of orders table
- Should combine into single aggregation
- Wasteful shuffles

**Solution:**
```python
# Combine all metrics in single aggregation
daily_sales = orders.groupBy("order_date").agg(
    F.sum("total_amount").alias("total_revenue"),
    F.count("order_id").alias("total_orders"),
    F.countDistinct("customer_id").alias("unique_customers"),
    F.avg("total_amount").alias("avg_order_value")
)
```

**Copilot Prompt Suggestions:**
- "Fix the rolling average window calculation"
- "Add year partitioning to cumulative sum"
- "Combine multiple aggregations into one for performance"

---

### **Step 6: Category Performance Analysis**

#### Issue #16: Double Counting from Wrong Join
**Problem:**
```python
category_sales = products.join(order_items, "product_id", "inner")
```
- Order items can have multiple rows per product (quantity)
- Join multiplies data incorrectly
- Should aggregate order_items first

**Solution:**
```python
# Aggregate order items first, then join
order_item_agg = order_items.groupBy("product_id").agg(
    F.sum(F.col("quantity") * F.col("unit_price") * 
          (1 - F.coalesce(F.col("discount_percent"), F.lit(0)) / 100)).alias("product_revenue"),
    F.sum("quantity").alias("quantity_sold")
)

category_sales = products.join(
    order_item_agg,
    "product_id",
    "inner"
).groupBy("category").agg(
    F.sum("product_revenue").alias("total_revenue"),
    F.sum("quantity_sold").alias("total_quantity")
)
```

#### Issue #17: Rank Without Proper Partitioning
**Problem:**
```python
F.rank().over(Window.orderBy(F.desc("total_revenue")))
```
- Ranks products globally across all categories
- Should rank within each category
- Missing dense_rank for tied values

**Solution:**
```python
# Rank within each category
windowSpec = Window.partitionBy("category").orderBy(F.desc("total_revenue"))

category_top_products = products.join(product_revenue, "product_id") \
    .withColumn("rank", F.dense_rank().over(windowSpec)) \
    .filter(F.col("rank") <= 5)
```

**Copilot Prompt Suggestions:**
- "Fix double counting in category sales calculation"
- "Add category partitioning to product ranking"

---

## 🎓 Complete Fixed Version Summary

### Key Fixes Required:

1. **Data Loading**: Add predicate pushdown, column pruning, partitioning, and caching
2. **Cohort Analysis**: Fix cohort assignment, period calculation, and retention metrics
3. **Product Affinity**: Eliminate duplicate pairs, add proper metrics, optimize joins
4. **CLV Calculation**: Filter invalid orders, fix lifespan logic, handle edge cases
5. **Sales Dashboard**: Fix window functions, add partitioning, combine aggregations
6. **Category Analysis**: Prevent double counting, add proper ranking

### Performance Improvements:
- Reduced full table scans from 15+ to 4
- Added broadcast joins where appropriate
- Implemented proper caching strategy
- Combined multiple aggregations
- Added partition-level filtering

### Data Quality Enhancements:
- Null handling in all calculations
- Edge case handling for new customers
- Status filtering for valid orders
- Division by zero protection
- Data validation checks

---

## 🚀 Extension Exercises

Once you've debugged the pipeline, try these advanced challenges:

### 1. **Add Comprehensive Data Quality Checks**
```python
# Use Copilot to generate:
- Schema validation
- Data freshness checks
- Completeness metrics
- Anomaly detection
```

### 2. **Implement Slowly Changing Dimensions**
Handle customer attribute changes over time

### 3. **Add Incremental Processing**
Modify pipeline to process only new/changed data

### 4. **Create Data Quality Dashboard**
Build visualizations for data quality metrics

### 5. **Implement A/B Test Analysis**
Add statistical significance testing for experiments

### 6. **Add Machine Learning Features**
Create feature engineering pipeline for churn prediction

### 7. **Optimize for Production**
- Add comprehensive error handling
- Implement checkpoint/restart logic
- Add detailed logging and monitoring
- Create data lineage tracking

---

## 💡 Learning Tips

1. **Start with Understanding**: Ask Copilot to explain each section before debugging
2. **Test Incrementally**: Fix one issue at a time and validate results
3. **Compare Approaches**: Ask Copilot for multiple solutions and compare them
4. **Think About Edge Cases**: What happens with null data? New customers? No orders?
5. **Consider Performance**: Ask Copilot to explain the query execution plan
6. **Add Tests**: Create unit tests for each transformation with Copilot's help

---

## 📊 Expected Results After Fixes

### Cohort Retention Table:
- Each customer appears in exactly one cohort
- Period 0 has 100% retention by definition
- Retention decreases over time naturally
- No null or negative values

### Product Affinity:
- No (A, A) pairs
- No duplicate (A, B) and (B, A) pairs
- Meaningful lift scores (lift > 1 indicates positive affinity)
- Reasonable support levels

### CLV Distribution:
- All customers included (even those without orders)
- No zero lifespans for active customers
- Realistic projected values
- Proper handling of new vs. established customers

### Sales Dashboard:
- Smooth moving averages without gaps
- Correct YTD calculations that reset each year
- Accurate customer counts (unique per day)
- Proper growth rate calculations

Good luck debugging! Remember: GitHub Copilot is your debugging partner - use it actively throughout the process! 🚀
