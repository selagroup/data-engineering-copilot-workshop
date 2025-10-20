# Data Engineering Copilot Workshop

A hands-on workshop for learning data engineering with GitHub Copilot, featuring SQL, Pandas, PySpark, and Apache Airflow.

## 🏗️ Architecture

The project uses a containerized data engineering stack:

- **PostgreSQL**: Primary relational database with `raw` and `analytics` schemas
- **Redis**: Caching and temporary data storage
- **MinIO**: S3-compatible object storage for raw data files

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Git

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd data-engineering-copilot-workshop
   ```

2. **Start Docker services**
   ```bash
   docker-compose up -d
   ```

3. **Create virtual environment and install dependencies**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python setup/fix_db.py
   ```
   
   This script will:
   - Generate fresh mock data
   - Drop and recreate all tables with correct schema
   - Load data from CSV files
   - Create analytics views
   - Reset sequence counters

5. **Verify the setup**
   ```bash
   python verify_setup.py
   ```
   
   This will check:
   - Database connectivity
   - Schema and table structure
   - Data availability
   - Analytics views
   - Sample queries

### Database Access

- **Host**: localhost
- **Port**: 5432
- **Database**: workshop_db
- **Username**: dataeng
- **Password**: copilot123

Connection string:
```
postgresql://dataeng:copilot123@localhost:5432/workshop_db
```

## 📊 Database Schema

### Raw Schema (`raw`)

- **customers**: Customer information (1,000 records)
- **products**: Product catalog (200 records)
- **orders**: Order transactions (5,000 records)
- **order_items**: Individual items per order (~15,000 records)

### Analytics Schema (`analytics`)

Views for reporting:
- **customer_summary**: Customer lifetime value and metrics
- **product_performance**: Product sales analytics
- **monthly_sales**: Monthly aggregated sales data

See `schema/database_schema.sql` for complete schema definition.

## 🎓 Workshop Exercises

### Exercise 1: SQL Generation (`exercises/01_sql_exercise.py`)
Learn to write effective comments that generate SQL queries with Copilot.

### Exercise 2: Pandas Operations (`exercises/02_pandas_exercise.py`)
Data manipulation and transformation using Pandas.

### Exercise 3: PySpark Transformations (`exercises/03_pyspark_exercise.py`)
Big data processing with PySpark.

### Exercise 4: Airflow DAGs (`exercises/04_airflow_exercise.py`)
Workflow orchestration and scheduling.

## 🔧 Troubleshooting

### Database Issues

If you encounter database schema errors:

```bash
python setup/fix_db.py
```

This will completely reset the database with the correct schema.

### Reset Everything

To start fresh:

```bash
# Stop and remove containers
docker-compose down -v

# Restart services
docker-compose up -d

# Reinitialize database
python setup/fix_db.py
```

## 📁 Project Structure

```
├── docker-compose.yml          # Container orchestration
├── requirements.txt            # Python dependencies
├── schema/                     # Database schema definitions
│   ├── database_schema.sql     # Table definitions (source of truth)
│   ├── create_views.py         # Analytics view creation
│   └── schema_context.md       # Schema documentation
├── setup/                      # Setup and initialization scripts
│   ├── init_db.sql            # Initial DB setup (run by Docker)
│   ├── fix_db.py              # Database reset and reload script
│   ├── generate_mock_data.py  # Mock data generation
│   └── sample_data/           # CSV data files
├── src/                        # Core application code
│   ├── data_pipeline/         # ETL pipeline components
│   │   ├── extractors.py      # Data extraction
│   │   ├── transformers.py    # Data transformation
│   │   └── loaders.py         # Data loading
│   ├── templates/             # SQL and other templates
│   └── utils/                 # Utility functions
│       ├── db_connection.py   # Database connection helpers
│       └── data_quality.py    # Data quality checks
├── exercises/                  # Workshop exercises
├── notebooks/                  # Jupyter notebooks for demos
└── tests/                      # Test suite
```

## 🔑 Key Conventions

1. **Database Schema**: Always refer to `schema/database_schema.sql` as the source of truth
2. **SQL Queries**: Use the `raw` schema for raw data, `analytics` schema for reporting
3. **Database Connections**: Use functions in `src/utils/db_connection.py`
4. **Templated SQL**: Store SQL templates in `src/templates/sql_templates/`

## 📝 Development Workflow

1. Start with exercises in order (01 → 04)
2. Use GitHub Copilot to generate code from comments
3. Test your solutions by running the exercise files
4. Check the `solutions/` directory if you get stuck
5. Experiment with notebooks for interactive exploration

## 🤝 Contributing

When making changes:
1. Keep `schema/database_schema.sql` as the authoritative schema
2. Update `setup/fix_db.py` if schema changes are needed
3. Regenerate mock data if adding new tables or columns
4. Test setup process from scratch before committing

## 📚 Additional Resources

- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)

## 📄 License

This project is for educational purposes.
