# All dimensions and styling/positioning throughout this app are completely arbitary and only meant for MY laptop.

from utilities import *
from dash import Dash, html, dcc, callback, Output, Input, State, ctx
from candlemaker import candle_maker, add_entry_tp_sl
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

app = Dash(__name__)
app.title = "ZakuroSoda/Quant"
app.layout = html.Div(
    [
        html.H1("ZakuroSoda/Quant Terminal"),
        dcc.DatePickerSingle(
            id='date-picker',
            display_format='DD/MM/YYYY',
            month_format='MMMM YYYY',
            min_date_allowed=df['date'].min(),
            max_date_allowed=df['date'].max(),
            initial_visible_month=df['date'].max(),
            date=df['date'].max(),
        ),
        html.Pre(id='entry-text'),
        html.Pre(id='levels-text', children="Selected Data"),

        html.Div([
            html.Button('BUY', id='buy-button', n_clicks=0, className='buy-button'),
            html.Button('SELL', id='sell-button', n_clicks=0, className='sell-button'),
        ], style={'display': 'flex', 'justify-content': 'space-between', 'width': '180px', 'margin': '0 auto'}),

        dcc.Graph(
            id='candlestick-chart',
            figure=fig,
            config={'displayModeBar': True, 'scrollZoom': False, 'displaylogo': False}
        ),

        dcc.Store(id='trade-direction', data="BUY"),
        dcc.Store(id='entry-price', data=0),
        dcc.Store(id='stop-loss', data=0),
        dcc.Store(id='take-profit', data=0),
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

# when it comes to implementing the trade entry with TP / SL, we'll need to be smart with Dash/PLotly.
# using "Selection Data" seems to be the only way to select arbitrary (empty) points on the graph that are non-data-points.
# https://community.plotly.com/t/selected-data-that-is-not-tied-to-points-in-a-graph/4708/4
# https://github.com/plotly/dash-core-components/pull/33
# There is no "Click Data" event for empty/blank spaces in the graph. We can only get "Click Data" for data points.
# https://community.plotly.com/t/adding-click-event-to-the-blank-space-of-the-plot/19077
# https://github.com/plotly/plotly.js/issues/2696 The issue is somehow still since 2018.

# additionally, we can't split this up into smaller callbacks since different callbacks can't share the same input/output.
@callback(
    Output('trade-direction', 'data'),
    Output('entry-price', 'data'),
    Output('entry-text', 'children'),

    Input('buy-button', 'n_clicks'),
    Input('sell-button', 'n_clicks'),
    Input('candlestick-chart', 'clickData'),

    State('trade-direction', 'data'),
    State('entry-price', 'data'),
)
def handle_all_trade_actions(buy_clicks, sell_clicks, clickData, trade_direction, entry_price):
    if not ctx.triggered:
        return "BUY", 0, "To start a trade, click on the entry candle."
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'buy-button':
        return "BUY", entry_price, f"Buying at {entry_price}."
    elif trigger_id == 'sell-button':
        return "SELL", entry_price, f"Selling at {entry_price}."
    
    elif trigger_id == 'candlestick-chart':
        new_entry_price = clickData['points'][0]['close']
        if trade_direction == "BUY":
            return trade_direction, new_entry_price, f"Buying at {new_entry_price}."
        else:
            return trade_direction, new_entry_price, f"Selling at {new_entry_price}."

@callback(
    Output('stop-loss', 'data'),
    Output('take-profit', 'data'),
    Output('levels-text', 'children'),
    Input('candlestick-chart', 'selectedData'),
    State('trade-direction', 'data'),
    State('entry-price', 'data'),
    State('candlestick-chart', 'figure')
)
def set_levels(selectedData, trade_direction, entry_price, fig):
    if selectedData is None or entry_price == 0:
        return 0, 0, "You may set levels after determining entry."
    
    if trade_direction == "BUY":
        sl = selectedData['range']['y'][0]
        tp = selectedData['range']['y'][1]
        rr = (tp - entry_price) / (entry_price - sl)
    else:
        sl = selectedData['range']['y'][1]
        tp = selectedData['range']['y'][0]
        rr = (entry_price - tp) / (sl - entry_price)

    #TODO: For immediate execution on the next commit
    # we need to put the TradingView style green and red rectangle to show the levels.
    # however this will require us to Output to figure, so we might need to combine with the date figure updating

    return sl, tp, f"SL: {sl:.4f}, TP: {tp:.4f}, RR: {rr:.2f}"

if __name__ == '__main__':
    app.run(debug=False)
