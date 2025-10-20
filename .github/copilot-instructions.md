<!-- #copilot----
applyTo: '**'
---
## Project Overview & Architecture

The core logic is in the `src/` directory and follows an ETL (Extract, Transform, Load) pattern:
- `src/data_pipeline/extractors.py`: Scripts to extract data from various sources.
- `src/data_pipeline/transformers.py`: Scripts for data transformation and business logic.
- `src/data_pipeline/loaders.py`: Scripts to load data into the PostgreSQL database.

## Developer Workflow

### Environment Setup
1.  **Start Services:** Run `docker-compose up -d` to start the PostgreSQL, Redis, and MinIO services.
2.  **Install Dependencies:** Create a virtual environment and run `pip install -r requirements.txt` to install the required Python packages.

### Database Initialization
- The database schema is defined in `schema/database_schema.sql`. This is the source of truth for all table structures and views.
- To initialize the database with tables and mock data, use the scripts in the `setup/` directory. `setup/init_db.sql` is run automatically by the postgres container. `setup/generate_mock_data.py` can be run to populate the database.

### Running Tests
- The project uses `pytest` for testing.
- Tests are located in the `tests/` directory.
- Run tests using the `pytest` command from the root of the project.

## Conventions & Patterns

### SQL Queries
- **Always refer to `schema/database_schema.sql`** when writing or modifying SQL queries to ensure you are using the correct table and column names.
- The `raw` schema is for raw, unprocessed data.
- The `analytics` schema contains views for reporting and should be queried for analytical purposes.

### Templated SQL
- SQL queries can be templated using Jinja2. Templates are stored in `src/templates/sql_templates/`. This is useful for generating dynamic queries.

### Database Connections
- All database connection logic should be handled by functions in `src/utils/db_connection.py`. Do not write raw connection strings in your code. -->