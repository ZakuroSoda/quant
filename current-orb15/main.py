from utilities import load_file
from candlemaker import candle_maker, add_entry_tp_sl

import dash
from dash import Dash, html, dcc, callback, Output, Input, State, ctx
from plotly import graph_objects as go
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

# display the last day by default
df_working = df_regular_hours[df_regular_hours['date'] == df_regular_hours['date'].unique()[-1]].reset_index(drop=True)

fig = candle_maker(df_working)

app = Dash(__name__)
app.title = "ZakuroSoda/Quant"
app.layout = html.Div(
    [
        html.Div([
            html.H1("ZakuroSoda/Quant Terminal"),
            dcc.DatePickerSingle(
                id='date-picker',
                display_format='DD/MM/YYYY',
                month_format='MMMM YYYY',
                min_date_allowed=df['date'].min(),
                max_date_allowed=df['date'].max(),
                initial_visible_month=df['date'].max(),
                date=df['date'].max(),
            )
        ], className='top'),
        html.Pre(id='levels-text'),

        html.Div([
            html.Button('BUY', id='buy-button', n_clicks=0, className='buy-button'),
            html.Pre(id='entry-text', children="XXX.XXXX"),
            html.Button('SELL', id='sell-button', n_clicks=0, className='sell-button'),
        ], className='buy-sell-buttons'),

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
    Output('buy-button', 'className'),
    Output('sell-button', 'className'),

    Input('buy-button', 'n_clicks'),
    Input('sell-button', 'n_clicks'),
    State('candlestick-chart', 'figure'),
)
def handle_all_trade_actions(buy_clicks, sell_clicks, current_fig):
    if not ctx.triggered:
        return "BUY", 0, "xxx.xxxx", "buy-button", "sell-button"
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    data = current_fig['data'][0]
    num_candles = len(data['x'])
    last_close = data['close']['_inputArray'][str(num_candles - 1)]

    if trigger_id == 'buy-button':
        return "BUY", last_close, last_close, "buy-button selected", "sell-button"
    elif trigger_id == 'sell-button':
        return "SELL", last_close, last_close, "buy-button", "sell-button selected"
   
@callback(
    Output('candlestick-chart', 'figure'),
    Output('stop-loss', 'data'),
    Output('take-profit', 'data'),
    Output('levels-text', 'children'),
    Input('date-picker', 'date'),
    Input('candlestick-chart', 'selectedData'),
    State('trade-direction', 'data'),
    State('entry-price', 'data'),
    State('candlestick-chart', 'figure')
)
def update_chart_and_levels(date_selected, selectedData, trade_direction, entry_price, current_fig):
    if not ctx.triggered:
        return current_fig, 0, 0, "You may set levels after determining entry."
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'date-picker':
        df_working = df_regular_hours[df_regular_hours['date'] == date.fromisoformat(date_selected)].reset_index(drop=True)
        # TODO: may want to return a 'Invalid Date' alert when there is no data and revert the date selection back
        new_fig = candle_maker(df_working)
        return new_fig, dash.no_update, dash.no_update, dash.no_update
    
    elif trigger_id == 'candlestick-chart':
        if selectedData is None or entry_price == 0:
            return current_fig, 0, 0, "You may set levels after determining entry."
        
        if trade_direction == "BUY":
            sl = selectedData['range']['y'][0]
            tp = selectedData['range']['y'][1]
            rr = (tp - entry_price) / (entry_price - sl)
        else:
            sl = selectedData['range']['y'][1]
            tp = selectedData['range']['y'][0]
            rr = (entry_price - tp) / (sl - entry_price)
        
        fig = go.Figure(current_fig)
        fig = add_entry_tp_sl(fig, entry_price, sl, tp)

        sl_percent = abs((entry_price - sl) / entry_price) * 100
        tp_percent = abs((tp - entry_price) / entry_price) * 100

        return fig, sl, tp, f"SL: {sl:.4f} / {sl_percent:.2f}%, TP: {tp:.4f} / {tp_percent:.2f}%, RR: {rr:.2f}"
    
        #TODO: Combine the two callbacks so that we can update TP/SL even when we simply switch our trading direction etc.
        #TODO: After combining, make sure that when we change dates, we clear everything, clear the trading direction etc.

if __name__ == '__main__':
    app.run(debug=False)
