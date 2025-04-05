from utilities import *
from dash import Dash, html, dcc, callback, Output, Input
from candlemaker import candle_maker
from datetime import date
import json

df = load_file("./Data/SPY_5min_merged.csv", date_format="%Y-%m-%d %H:%M:%S")
print(df.dtypes)
print(df.head())
print(df.tail())

df['date'] = df['timestamp'].dt.date
df['hour'] = df['timestamp'].dt.hour
df['minute'] = df['timestamp'].dt.minute
df['time_val'] = df['hour'] * 100 + df['minute']  # Creates time in HHMM format

df_regular_hours = df[(df['time_val'] >= 930) & (df['time_val'] <= 1555)]

print(df.shape)
print(df_regular_hours.shape)
print(f"Trading Days Available: {df_regular_hours['date'].nunique()}")


TRADING_DAY_TO_DISPLAY = -1
df_working = df_regular_hours[df_regular_hours['date'] == df_regular_hours['date'].unique()[TRADING_DAY_TO_DISPLAY]].reset_index(drop=True)

fig = candle_maker(df_working)

app = Dash(__name__)
app.layout = html.Div(
    [
        html.H1("KKK Quant Terminal"),
        dcc.DatePickerSingle(
            id='date-picker',
            display_format='DD/MM/YYYY',
            month_format='MMMM YYYY',
            min_date_allowed=df['date'].min(),
            max_date_allowed=df['date'].max(),
            initial_visible_month=df['date'].max(),
            date=df['date'].max(),
        ),
        dcc.Graph(
            id='candlestick-chart',
            figure=fig,
            config={'displayModeBar': True, 'scrollZoom': False, 'displaylogo': False}
        ),
        html.H1(id='click-data'),
    ],
)

@callback(
    Output('candlestick-chart', 'figure'),
    Input('date-picker', 'date')
)
def update_candlestick(date_selected):
    df_working = df_regular_hours[df_regular_hours['date'] == date.fromisoformat(date_selected)].reset_index(drop=True)
    # TODO: may want to return a 'Invalid Date' alert when there is no data and revert the date selection back
    fig = candle_maker(df_working)
    return fig

@callback(
    Output('click-data', 'children'),
    Input('candlestick-chart', 'clickData'))
def display_click_data(clickData):
    return str(clickData)

if __name__ == '__main__':
    app.run(debug=False)
