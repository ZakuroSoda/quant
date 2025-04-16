import pandas as pd

def load_file(file_path: str, date_format: str = "%Y-%m-%d"):
    df = pd.read_csv(file_path, parse_dates=['timestamp'], date_format=date_format)
    df.sort_values(by='timestamp', inplace=True)
    return df