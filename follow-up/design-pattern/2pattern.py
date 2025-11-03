import pandas as pd
import sqlalchemy as sa

def load_table(source: str, path_or_conn: str, table: str = None) -> pd.DataFrame:
    if source == "csv":
        return pd.read_csv(path_or_conn)
    elif source == "parquet":
        return pd.read_parquet(path_or_conn)
    elif source == "postgres":
        engine = sa.create_engine(path_or_conn)
        return pd.read_sql_table(table, con=engine)
    else:
        raise ValueError("unknown source")
