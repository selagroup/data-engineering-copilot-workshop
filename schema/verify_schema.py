import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://dataeng:copilot123@localhost:5432/workshop_db')

schemas = ['raw', 'analytics']
tables = {
    'raw': ['customers', 'products', 'orders', 'order_items'],
}
views = {
    'analytics': ['customer_summary', 'product_performance', 'monthly_sales'],
}

def check_table_columns(schema, table):
    q = f"""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = '{schema}' AND table_name = '{table}'
        ORDER BY ordinal_position
    """
    df = pd.read_sql(q, engine)
    print(f"\nTable: {schema}.{table}")
    print(df.to_string(index=False))

def check_view_columns(schema, view):
    q = f"""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = '{schema}' AND table_name = '{view}'
        ORDER BY ordinal_position
    """
    df = pd.read_sql(q, engine)
    print(f"\nView: {schema}.{view}")
    print(df.to_string(index=False))

if __name__ == "__main__":
    # Check schemas
    for schema in schemas:
        q = f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{schema}'"
        df = pd.read_sql(q, engine)
        if not df.empty:
            print(f"Schema exists: {schema}")
        else:
            print(f"[ERROR] Schema missing: {schema}")

    # Check tables
    for schema, tbls in tables.items():
        for tbl in tbls:
            q = f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}' AND table_name = '{tbl}'"
            df = pd.read_sql(q, engine)
            if not df.empty:
                print(f"Table exists: {schema}.{tbl}")
                check_table_columns(schema, tbl)
            else:
                print(f"[ERROR] Table missing: {schema}.{tbl}")

    # Check views
    for schema, vws in views.items():
        for vw in vws:
            q = f"SELECT table_name FROM information_schema.views WHERE table_schema = '{schema}' AND table_name = '{vw}'"
            df = pd.read_sql(q, engine)
            if not df.empty:
                print(f"View exists: {schema}.{vw}")
                check_view_columns(schema, vw)
            else:
                print(f"[ERROR] View missing: {schema}.{vw}")
