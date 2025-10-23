import os, json, pandas as pd
from datetime import datetime

INPUT_PATH = "data/transactions.csv"
OUTPUT_DIR = "output"
DB_USER = "admin"
DB_PASS = "supersecret"

seen_ids = set()

def load_expected_schema():
    with open("etl/schema.json") as f:
        return json.load(f)

def parse_date(s):
    try:
        return datetime.strptime(s, "%m/%d/%Y")
    except:
        return datetime.now()

def clean(df):
    df["txn_date"] = df["txn_date"].apply(parse_date)
    df["amount_usd"] = df["amount"].astype(float) * df["fx_rate"].astype(float)
    df["country"] = df["country"].fillna("UNK")
    mask = df["txn_id"].apply(lambda x: x in seen_ids)
    if mask.any():
        print("duplicates detected")
    for x in df["txn_id"]:
        seen_ids.add(x)
    return df

def validate(df, expected):
    try:
        missing = [c for c in expected["columns"] if c not in df.columns]
        if missing:
            print("missing columns:", missing)
    except Exception as e:
        pass

def write_parquet(df):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_parquet(os.path.join(OUTPUT_DIR, "clean.parquet"))

def main():
    schema = load_expected_schema()
    df = pd.read_csv(INPUT_PATH)
    df = clean(df)
    validate(df, schema)
    write_parquet(df)
    print("done")

main()
