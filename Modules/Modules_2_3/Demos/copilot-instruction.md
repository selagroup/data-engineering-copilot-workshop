---
applyTo: "*"
---
# GitHub Copilot Instructions for Data Engineering Workshop

## Project Overview
This is a data engineering workshop focused on foundational data engineering concepts using Python, SQL, and PySpark in a local development environment with Azure PostgreSQL as the backend database.

## Tech Stack
- **Database**: Azure PostgreSQL (managed database service)
- **Languages**: Python 3.11+, SQL, PySpark
- **Frameworks**: PySpark (local mode), pandas, psycopg2
- **Storage**: Local file system (CSV, Parquet files), PostgreSQL database
- **Tools**: Jupyter notebooks, pytest

## Workshop Environment
⚠️ **This is a LOCAL workshop environment for learning purposes:**
- PySpark runs in **local mode** (`master("local[*]")`)
- Database credentials in `.env` files (simplified for workshop)
- Sample data stored locally in `setup/sample_data/`
- Focus on learning core concepts, not production deployment

---

## Code Generation Guidelines

### Python Code Standards
- Always use **type hints** for function parameters and return values
- Follow **PEP 8** style guidelines
- Include comprehensive **docstrings** (Google style preferred)
- Use **f-strings** for string formatting
- Prefer **pathlib** over os.path for file operations
- Include **logging** statements at appropriate levels (INFO, WARNING, ERROR)

Example:
```python
from typing import Dict, List
import logging

def transform_data(input_df: pd.DataFrame, config: Dict[str, str]) -> pd.DataFrame:
    """
    Transform input DataFrame according to business rules.
    
    Args:
        input_df: Source DataFrame to transform
        config: Configuration dictionary with transformation parameters
        
    Returns:
        Transformed DataFrame ready for loading
    """
    logging.info(f"Starting transformation with {len(input_df)} rows")
    # transformation logic here
    return transformed_df
```

### SQL Standards
- Use **UPPERCASE** for SQL keywords (SELECT, FROM, WHERE, JOIN)
- Use **snake_case** for table and column names
- Always include **explicit column names** (avoid SELECT *)
- Add comments explaining complex logic
- Use CTEs (Common Table Expressions) for readability

Example:
```sql
-- Calculate daily sales metrics with customer segmentation
WITH daily_sales AS (
    SELECT 
        DATE(order_date) AS sale_date,
        customer_id,
        SUM(order_amount) AS daily_total
    FROM orders
    WHERE order_date >= DATEADD(day, -30, GETDATE())
    GROUP BY DATE(order_date), customer_id
)
SELECT * FROM daily_sales;
```

### PySpark Standards
- Use **DataFrame API** over RDD when possible
- Include **.cache()** or **.persist()** for reused DataFrames
- Always specify **schema explicitly** when reading data
- Use **column expressions** instead of string column names
- Include **null handling** in transformations

Example:
```python
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

schema = StructType([
    StructField("customer_id", StringType(), False),
    StructField("order_amount", IntegerType(), True)
])

# Read from local file system (workshop environment)
df = spark.read.schema(schema).parquet("data/orders/*.parquet")
df = df.withColumn("order_amount", F.coalesce(F.col("order_amount"), F.lit(0)))
```

---

## Data Engineering Best Practices

### Pipeline Design
- Always implement **incremental/delta loading** patterns
- Include **watermark columns** (e.g., last_modified_date, processing_timestamp)
- Use **partitioning** for large datasets (by date, region, etc.)
- Implement **idempotency** - pipelines should be safe to re-run
- Add **data quality checks** at each stage (completeness, accuracy, validity)

### Error Handling
- Use **try-except blocks** with specific exception types
- Log errors with **context** (what was being processed when error occurred)
- Implement **retry logic** for transient failures (with exponential backoff)
- Create **dead letter queues** or error tables for failed records
- Never silently swallow exceptions

Example:
```python
import psycopg2
import time
import logging

def execute_query_with_retry(connection_string: str, query: str, max_retries: int = 3) -> None:
    """Execute database query with retry logic for transient failures."""
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(connection_string)
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            logging.info(f"Successfully executed query")
            return
        except psycopg2.OperationalError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logging.warning(f"Query failed, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
            else:
                logging.error(f"Failed to execute query after {max_retries} attempts: {e}")
                raise
        finally:
            if 'conn' in locals():
                conn.close()
```

### Data Validation
- Validate **schema** before processing
- Check for **null/missing values** in critical columns
- Verify **data types** match expectations
- Validate **business rules** (e.g., amounts > 0, valid date ranges)
- Log **validation metrics** (rows processed, rows rejected, rejection reasons)

Example:
```python
def validate_orders(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Validate orders DataFrame and separate valid/invalid records.
    
    Returns:
        Tuple of (valid_df, invalid_df)
    """
    required_cols = ['order_id', 'customer_id', 'order_date', 'amount']
    
    # Check required columns exist
    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Validate business rules
    valid_mask = (
        df['order_id'].notna() &
        df['customer_id'].notna() &
        df['amount'] > 0 &
        df['order_date'] <= pd.Timestamp.now()
    )
    
    valid_df = df[valid_mask]
    invalid_df = df[~valid_mask]
    
    logging.info(f"Validation: {len(valid_df)} valid, {len(invalid_df)} invalid records")
    
    return valid_df, invalid_df
```

---

## Database Connection Guidelines

### PostgreSQL Connection Pattern
Use environment variables for database credentials:

```python
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_db_connection():
    """Create PostgreSQL connection using environment variables."""
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT', '5432')
    )
```

### .env File Structure
```bash
# Database Configuration
DB_HOST=your-server.postgres.database.azure.com
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
DB_PORT=5432
```

⚠️ **Important**: 
- Never commit `.env` files to source control
- Add `.env` to `.gitignore`
- Use `.env.example` as a template without actual credentials

---

## Workshop Database Schema

The workshop uses a retail database with the following structure:

### Raw Schema (`raw`)
- `customers`: Customer information
- `products`: Product catalog
- `orders`: Order headers
- `order_items`: Order line items

### Analytics Schema (`analytics`)
- Views built on top of raw tables
- Pre-aggregated metrics for analysis

Use the schema context file at `schema/schema_context.md` for detailed information.

---

## Azure-Specific Guidelines

### Authentication (For Production Reference Only)
⚠️ **Workshop uses simplified authentication** - the patterns below are for production reference:

- **Prefer Managed Identity** over connection strings/keys
- Use **Azure Key Vault** for secrets management
- Never hardcode credentials in code
- Use **Azure SDK DefaultAzureCredential** for local development

Example (production pattern):
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Production pattern - NOT used in this workshop
credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://your-keyvault.vault.azure.net/", credential=credential)
db_password = client.get_secret("db-password").value
```

### Resource Naming
Follow Azure naming conventions (for production reference):
- Use **lowercase** with hyphens for resource names
- Include **environment prefix** (dev, test, prod)
- Include **resource type abbreviation**
- Keep names under 24 characters where possible

Examples:
- Storage Account: `stdevdataeng001`
- PostgreSQL Server: `psql-dev-workshop-001`
- Key Vault: `kv-dev-dataeng`

---

## Workshop-Specific Guidelines

### Educational Code
- Include **detailed comments** explaining "why" not just "what"
- Add **inline documentation** for complex transformations
- Provide **before/after examples** of data transformations
- Include **sample data generators** for testing
- Create **step-by-step notebooks** with clear sections

### Example Structure
```python
# WORKSHOP EXAMPLE: Customer Segmentation Pipeline
# 
# Learning objectives:
# 1. Read data from PostgreSQL database
# 2. Perform data quality checks
# 3. Apply business logic for segmentation
# 4. Write results back to database

# Step 1: Import required libraries
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import os
from dotenv import load_dotenv

load_dotenv()

# Step 2: Initialize Spark session (local mode for workshop)
spark = SparkSession.builder \
    .appName("CustomerSegmentation") \
    .master("local[*]") \
    .getOrCreate()

# Step 3: Read customer data from PostgreSQL
jdbc_url = f"jdbc:postgresql://{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
customers_df = spark.read \
    .format("jdbc") \
    .option("url", jdbc_url) \
    .option("dbtable", "raw.customers") \
    .option("user", os.getenv('DB_USER')) \
    .option("password", os.getenv('DB_PASSWORD')) \
    .option("driver", "org.postgresql.Driver") \
    .load()

# Step 4: Calculate customer metrics
# Business rule: Segment based on total purchase amount
segmented_df = customers_df \
    .groupBy("customer_id") \
    .agg(
        F.sum("order_amount").alias("total_spent"),
        F.count("order_id").alias("order_count")
    ) \
    .withColumn(
        "segment",
        F.when(F.col("total_spent") > 10000, "Premium")
         .when(F.col("total_spent") > 5000, "Gold")
         .when(F.col("total_spent") > 1000, "Silver")
         .otherwise("Bronze")
    )

# Step 5: Write results to analytics schema
segmented_df.write \
    .format("jdbc") \
    .option("url", jdbc_url) \
    .option("dbtable", "analytics.customer_segments") \
    .option("user", os.getenv('DB_USER')) \
    .option("password", os.getenv('DB_PASSWORD')) \
    .option("driver", "org.postgresql.Driver") \
    .mode("overwrite") \
    .save()

print(f"Segmentation complete. Processed {segmented_df.count()} customers")
```

### Sample Data Generation
Always include sample data generators for testing:

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_orders(num_records: int = 1000) -> pd.DataFrame:
    """
    Generate sample order data for workshop exercises.
    
    Args:
        num_records: Number of sample records to generate
        
    Returns:
        DataFrame with sample order data
    """
    np.random.seed(42)
    
    return pd.DataFrame({
        'order_id': [f'ORD{i:06d}' for i in range(num_records)],
        'customer_id': np.random.choice([f'CUST{i:04d}' for i in range(100)], num_records),
        'order_date': [
            datetime.now() - timedelta(days=np.random.randint(0, 365)) 
            for _ in range(num_records)
        ],
        'product_id': np.random.choice([f'PROD{i:03d}' for i in range(50)], num_records),
        'quantity': np.random.randint(1, 10, num_records),
        'unit_price': np.random.uniform(10, 500, num_records).round(2),
        'status': np.random.choice(['completed', 'pending', 'cancelled'], num_records, p=[0.8, 0.15, 0.05])
    })
```

---

## Configuration Management

### Use Environment Variables (.env files)
- Store **environment-specific settings** in `.env` files
- Never commit **secrets** to source control
- Use `.env.example` as a template without actual credentials
- Implement **configuration validation** at startup

Example .env structure:
```bash
# Database Configuration
DB_HOST=your-server.postgres.database.azure.com
DB_NAME=workshop_db
DB_USER=workshop_user
DB_PASSWORD=your_secure_password
DB_PORT=5432

# Processing Configuration
BATCH_SIZE=10000
MAX_RETRIES=3
TIMEOUT_SECONDS=300
```

Example loading configuration:
```python
import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass
class PipelineConfig:
    """Configuration for data pipeline."""
    db_host: str
    db_name: str
    db_user: str
    db_password: str
    batch_size: int
    max_retries: int
    
    @classmethod
    def from_env(cls) -> 'PipelineConfig':
        """Load configuration from environment variables."""
        return cls(
            db_host=os.getenv('DB_HOST'),
            db_name=os.getenv('DB_NAME'),
            db_user=os.getenv('DB_USER'),
            db_password=os.getenv('DB_PASSWORD'),
            batch_size=int(os.getenv('BATCH_SIZE', '10000')),
            max_retries=int(os.getenv('MAX_RETRIES', '3'))
        )
```

---

## Testing Guidelines

### Unit Tests
- Test **data transformations** with sample data
- Test **validation logic** with edge cases
- Mock **database connections** in unit tests
- Focus on testable, pure functions

Example:
```python
import pytest
import pandas as pd
from your_module import validate_orders

def test_validate_orders_rejects_negative_amounts():
    """Test that orders with negative amounts are rejected."""
    test_data = pd.DataFrame({
        'order_id': ['ORD001', 'ORD002'],
        'customer_id': ['CUST001', 'CUST002'],
        'order_date': [pd.Timestamp.now(), pd.Timestamp.now()],
        'amount': [100.0, -50.0]  # Second order has negative amount
    })
    
    valid_df, invalid_df = validate_orders(test_data)
    
    assert len(valid_df) == 1
    assert len(invalid_df) == 1
    assert invalid_df.iloc[0]['order_id'] == 'ORD002'
```

### Integration Tests
- Test **end-to-end pipelines** with test data
- Verify **data quality** in output
- Test **error handling** and recovery
- Use **separate test database** or schema

---

## Documentation Standards

### README Files
Every major component should have a README with:
- **Purpose** and overview
- **Prerequisites** and setup instructions
- **Usage examples**
- **Configuration** options
- **Troubleshooting** guide

### Code Comments
- Explain **business logic** and complex algorithms
- Document **assumptions** and constraints
- Include **TODO** comments for future improvements
- Reference **documentation** or tickets for context

### Notebooks
- Use **Markdown cells** to explain each section
- Include **visualizations** of results
- Add **interactive widgets** where appropriate
- Provide **exercise sections** for hands-on learning

---

## Common Patterns to Use

### Configuration Pattern
```python
from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

@dataclass
class PipelineConfig:
    """Configuration for data pipeline."""
    source_path: str
    target_path: str
    batch_size: int
    max_retries: int
    
    @classmethod
    def from_env(cls) -> 'PipelineConfig':
        """Load configuration from environment variables."""
        load_dotenv()
        return cls(
            source_path=os.getenv('SOURCE_PATH'),
            target_path=os.getenv('TARGET_PATH'),
            batch_size=int(os.getenv('BATCH_SIZE', '10000')),
            max_retries=int(os.getenv('MAX_RETRIES', '3'))
        )
```

### Logging Pattern
```python
import logging
from datetime import datetime

def setup_logging(log_level: str = "INFO") -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/pipeline_{datetime.now():%Y%m%d_%H%M%S}.log'),
            logging.StreamHandler()
        ]
    )
```

### Spark Session Pattern
```python
from pyspark.sql import SparkSession

def get_spark_session(app_name: str, config: dict = None) -> SparkSession:
    """
    Create or get existing Spark session for local workshop environment.
    
    Args:
        app_name: Name for the Spark application
        config: Optional dictionary of Spark configuration options
        
    Returns:
        Configured Spark session
    """
    builder = SparkSession.builder \
        .appName(app_name) \
        .master("local[*]")  # Local mode for workshop
    
    # Standard configurations for local mode
    default_config = {
        "spark.sql.adaptive.enabled": "true",
        "spark.sql.adaptive.coalescePartitions.enabled": "true",
        "spark.driver.memory": "4g",
        "spark.executor.memory": "4g"
    }
    
    if config:
        default_config.update(config)
    
    for key, value in default_config.items():
        builder = builder.config(key, value)
    
    return builder.getOrCreate()
```

---

## Performance Optimization

### PySpark Optimization (Local Mode)
- **Broadcast small DataFrames** in joins (< 10MB)
- Use **repartition** before expensive operations
- Avoid **collect()** on large datasets
- Use **persist()** with appropriate storage level
- Enable **Adaptive Query Execution (AQE)**
- For local mode, be mindful of **memory constraints**

### SQL Optimization (PostgreSQL)
- Use **indexes** for frequently queried columns
- Implement **WHERE clause filtering** early
- Use **EXPLAIN ANALYZE** to understand query plans
- Avoid **implicit type conversions**
- Use **batch operations** instead of row-by-row
- Leverage PostgreSQL **COPY** command for bulk loads

---

## Security Considerations

- **Never log** sensitive data (PII, credentials)
- Use **row-level security** where appropriate
- Implement **data masking** for non-production environments
- Audit **data access patterns**
- Follow **least privilege** principle for service accounts

---

## Questions to Ask Before Generating Code

When a user requests code generation, consider asking:

1. **What environment is this for?** (local workshop vs production)
2. **What's the expected data volume?** (affects design decisions)
3. **Should this connect to PostgreSQL or work with local files?**
4. **Should this handle incremental or full loads?**
5. **What error handling behavior is expected?**
6. **Are there existing schemas or can I design new ones?**
7. **Should this use PySpark or pandas?** (PySpark for large data, pandas for small)

---

## Example Responses

### When asked to create a data pipeline:
"I'll create a data pipeline with the following components:
1. **Data ingestion** from PostgreSQL/CSV with error handling
2. **Data validation** to ensure quality
3. **Transformation** logic with proper logging
4. **Output** to PostgreSQL or local files
5. **Logging** for observability

This will run in local mode using PySpark. Should I proceed with this design?"

### When asked to optimize code:
"I'll analyze the code for:
1. **Performance bottlenecks** (unnecessary operations, inefficient joins)
2. **Resource usage** (memory, compute for local environment)
3. **Code quality** (maintainability, testability)
4. **Best practices** alignment for workshop context

Let me review and provide specific optimization recommendations."

---

## Important Reminders for Workshop Context

⚠️ **Always remember this is a LOCAL workshop environment:**

1. **Spark**: Use `.master("local[*]")` not production clusters
2. **Database**: PostgreSQL connections via JDBC, not Azure Data Lake
3. **Files**: Local file paths, not `abfss://` URLs
4. **Authentication**: Connection strings from `.env`, not Managed Identity
5. **Scale**: Optimize for laptop-scale data, not production petabyte scale
6. **Focus**: Educational clarity over production complexity

**When generating code:**
- Include **educational comments** explaining concepts
- Keep examples **runnable on laptops**
- Use **simple, clear patterns** over complex enterprise patterns
- Reference the **actual database schema** in `schema/` directory
- Load credentials from **`.env` files** using `python-dotenv`

**Production patterns to mention but not implement:**
- Azure Key Vault integration
- Managed Identity authentication
- Azure Data Lake Storage Gen2
- Databricks/Synapse configurations
- Delta Lake (unless specifically teaching ACID concepts)

---

Remember: The goal is to write **production-ready, maintainable code** that demonstrates best practices while being educational and easy to understand.