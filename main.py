from utilities import *
from dash import Dash, html, dcc, callback, Output, Input
from candlemaker import candle_maker
from datetime import date

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

app = Dash()
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
    )]
)

@callback(
    Output('candlestick-chart', 'figure'),
    Input('date-picker', 'date')
)
def update_candlestick(date_selected):
    df_working = df_regular_hours[df_regular_hours['date'] == date.fromisoformat(date_selected)].reset_index(drop=True)
    fig = candle_maker(df_working)
    return fig

if __name__ == '__main__':
    app.run(debug=False)

# fig.show(config={'displayModeBar': True, 'scrollZoom': False, 'displaylogo': False})
