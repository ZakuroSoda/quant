import pandas as pd
import numpy as np
from math import exp

def load_file(file_path: str, date_format: str = "%Y-%m-%d"):
    """
    Loads a CSV file pulled from Alpha Vantage's DAILY series, returns a pandas DataFrame sorted by date
    """
    df = pd.read_csv(file_path, parse_dates=['timestamp'], date_format=date_format)
    df.sort_values(by='timestamp', inplace=True)
    return df

def merge_csvs(files: list, output_file: str = ""):
    merged_data = pd.DataFrame()
    for file in files:
        df = pd.read_csv(file)
        merged_data = pd.concat([merged_data, df], ignore_index=True)

    merged_data.reset_index(drop=True, inplace=True)
    merged_data["timestamp"] = pd.to_datetime(merged_data["timestamp"], format="%Y-%m-%d %H:%M:%S")
    merged_data.sort_values(by='timestamp', inplace=True)
    
    if output_file:
        merged_data.to_csv(output_file, index=False)

    return merged_data

def add_rsi(df: pd.DataFrame, interval: int = 14):
    """
    Adds the TradingView implementation of Relative Strength Index, return a pandas DataFrame with new column "rsi"
    The default sliding window interval is 14.
    """
    delta = df["close"].diff()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    _gain = up.ewm(com=(interval - 1), min_periods=interval).mean()
    _loss = down.abs().ewm(com=(interval - 1), min_periods=interval).mean()
    RS = _gain / _loss

    df['rsi'] = 100 - (100 / (1 + RS))
    return df

def add_alma(df: pd.DataFrame, column: str, window: int = 20):
    """
    Calculates the Arnaud-Legoux Moving Average for a column of numerical values. The column added is "colname_alma".
    The default sliding window interval is 20.
    """

    def calculate_alma(values: list, window: int = window, offset: float = 0.85, sigma: float = 6) -> float:
        m = int(offset * (window - 1))
        s = window / sigma
        weights = np.array([exp(-((k - m) ** 2) / (2 * (s ** 2))) for k in range(window)])
        if len(values) < window:
            return None
        weighted_sum = weights * values[-window:]
        alma = weighted_sum.sum() / weights.sum()
        return alma

    alma_values = []
    for i in range(len(df)):
        values = df[column][:i+1].values
        alma = calculate_alma(values, window)
        alma_values.append(alma)    

    df[f'{column}_alma'] = alma_values
    return df

def negative(value: int | float) -> int | float:
    return -value

def average(values: list) -> float:
    return round(sum(values) / len(values), 2)

def percent_change(before: int | float, after: int | float) -> float:
    return round(((after - before) / before) * 100, 2)

def write_to_file(file_path: str, content: str):
    with open(file_path, 'w') as file:
        file.write(content)

def close_trade(position: dict, row: dict, stats: dict):
    stats["total_trades"] += 1

    if position["type"] == "LONG":
        result = percent_change(position["entry"], row["close"]) # (final - entry) / entry
        
        log = f"Trade {stats["total_trades"]}: LONG @ {position['entry']} on {position['entry_date'].strftime('%d/%m/%y')} CLOSED @ {row["close"]} on {row["timestamp"].strftime('%d/%m/%y')} for P/L of {result:.2f}%\n"

    elif position["type"] == "SHORT":
        result = negative(percent_change(position["entry"], row["close"])) # (entry - final) / entry

        log = f"Trade {stats['total_trades']}: SHORT @ {position['entry']} on {position['entry_date'].strftime('%d/%m/%y')} CLOSED @ {row['close']} on {row['timestamp'].strftime('%d/%m/%y')} for P/L of {result:.2f}%\n"

    stats["profit_loss_log"].append(result)
    stats["winning_trades"] += 1 if result > 0 else 0

    return stats, log
    