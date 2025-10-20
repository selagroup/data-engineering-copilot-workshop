import pandas as pd
from etl.etl import clean

def test_clean_basic():
    df = pd.DataFrame({
        "txn_id": [1, 2],
        "txn_date": ["01/02/2024", "02/30/2024"],
        "amount": ["10", "20.5"],
        "fx_rate": ["3.5", "3.6"],
        "country": ["IL", None]
    })
    out = clean(df)
    assert "amount_usd" in out.columns
