


# 📌 `utils/io_helpers.py`

import os
import pandas as pd
from typing import Optional

DATA_DIR = "data_for_st"

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_csv_safe(path: str) -> Optional[pd.DataFrame]:
    try:
        return pd.read_csv(path)
    except Exception:
        return None

def path_in_data(*parts) -> str:
    ensure_data_dir()
    return os.path.join(DATA_DIR, *parts)

def has_forecasts() -> bool:
    return os.path.exists(path_in_data("forecast_2030_baseline.csv"))

def load_preprocessed_data():
    file_path = os.path.join("data_statistics", "final_with_indexes.csv")  
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found.")
    return pd.read_csv(file_path)