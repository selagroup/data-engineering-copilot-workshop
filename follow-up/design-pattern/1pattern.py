# preprocess.py (baseline - branching)
import pandas as pd

def impute_column(df: pd.DataFrame, col: str, method: str = "mean"):
    if method == "mean":
        df[col] = df[col].fillna(df[col].mean())
    elif method == "median":
        df[col] = df[col].fillna(df[col].median())
    elif method == "mode":
        df[col] = df[col].fillna(df[col].mode().iloc[0])
    else:
        raise ValueError("unknown method")
    return df

# usage
df = pd.DataFrame({"age":[20, None, 40], "income":[1000, 1200, None]})
df = impute_column(df, "age", method="mean")
df = impute_column(df, "income", method="median")