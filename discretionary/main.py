import plotly.graph_objects as go
from plotly.offline import iplot
import pandas as pd

df = pd.read_csv("./data/SPY_5min_merged.csv", parse_dates=['timestamp'], date_format="%Y-%m-%d %H:%M:%S")
df.sort_values(by='timestamp', inplace=True)

df = df.tail(100)

fig = go.Figure(data=[go.Candlestick(x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'])])
