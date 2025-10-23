import logging
import pandas as pd


def load_csv_to_dataframe(file_path: str):
    DF = pd.read_csv(file_path)
    logging.info(f"Loaded CSV file from {file_path} with shape {df.shape}")
    return DF


def validate_schema(DF, SCHEMA: dict):
    for column, dtype in SCHEMA.items():
        if column not in DF.columns:
            logging.error(f"Missing column: {column}")
            return False
        if not pd.api.types.is_dtype_equal(DF[column].dtype, dtype):
            logging.error(f"Column {column} has incorrect type: {DF[column].dtype}, expected: {dtype}")
            return False
    logging.info("DataFrame schema validation passed.")
    return True
    return True

def transform_sales_data(DF):
    DF['total_sales'] = DF['quantity_sold'] * DF['price_per_unit']
    logging.info("Transformed sales data by adding 'total_sales' column.")
    return DF

