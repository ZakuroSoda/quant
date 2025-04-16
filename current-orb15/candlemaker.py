import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# import random

def candle_maker(df_working):

    date_str = df_working['date'].iloc[0].strftime("%Y-%m-%d")
    dayofweek = df_working['date'].iloc[0].strftime('%a')
    opening_range = df_working.head(3)
    orh, orl = opening_range['high'].max(), opening_range['low'].min()
    ormid = (orh + orl) / 2
    or_interval = (orh - orl) / 2

    #  Set Custom Views (xrange and yrange)
    xrange = [df_working['timestamp'].iloc[0] - pd.Timedelta(minutes=5), df_working['timestamp'].iloc[-1] + pd.Timedelta(minutes=5)]
    padding = 0.05
    # y_min, y_max = df_working['low'].min(), df_working['high'].max()
    # I choose to set the y-axis range as such to eliminate trading bias when you are able to roughly see the direction from the axis
    y_min, y_max = orl - 4* or_interval, orh + 4* or_interval
    y_range = y_max - y_min
    yrange = [y_min - (y_range * padding), y_max + (y_range * padding)]

    # Set colors for candlestick
    colors = {
        'bearish_wick': '#FF6347',
        'bearish_body': '#FF6347',
        'bearish_border': '#CC503A',
        
        'bullish_body': '#32CD32',
        'bullish_wick': '#32CD32',
        'bullish_border': '#28A028',
        
        'background': '#FAFAD2',
        'foreground': '#228B22',
        'text': '#000000',
        'grid': '#D3D3D3'
    }

    fig = make_subplots()

    fig.add_shape(
        type="line",
        x0=date_str + " 09:30:00",
        x1=date_str + " 16:00:00",
        y0=orh,
        y1=orh,
        line=dict(
            color="#000000",
            width=1,
            dash="solid",
        ),
        name="ORH"
    )

    fig.add_shape(
        type="line",
        x0=date_str + " 09:30:00",
        x1=date_str + " 16:00:00",
        y0=orl,
        y1=orl,
        line=dict(
            color="#000000",
            width=1,
            dash="solid",
        ),
        name="ORL"
    )

    fig.add_shape(
        type="line",
        x0=date_str + " 09:30:00",
        x1=date_str + " 16:00:00",
        y0=ormid,
        y1=ormid,
        line=dict(
            color="#000000",
            width=1,
            dash="dash",
        ),
        name="OR50"
    )

    fig.add_shape(
        type="rect",
        x0=date_str + " 09:30:00",
        x1=date_str + " 16:00:00",
        y0=orl,
        y1=orh,
        fillcolor="rgba(214, 180, 252, 0.2)",
        line=dict(width=0),
        layer="below",
        name="OR"
    )

    fig.update_layout(
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        font={'color': colors['text'], 'family': 'Inconsolata', 'size': 15},
        title = f"SPY: {date_str} {dayofweek}", title_y = 0.95,

        xaxis=dict(
            type='date',
            rangeslider=dict(visible=False), # cleaner
            fixedrange=True,  # Allow zooming on x-axis
            # autorange=True, # this must be disabled IF we set an initial range window
            range=xrange,
            # rangebreaks no longer needed since we are plotting day by day
            # rangebreaks=[
            #     dict(bounds=["sat", "mon"]),  # Hide weekends
            #     dict(bounds=[17, 9], pattern="hour")  # Hide non-trading hours
            # ],
            showgrid=False
        ),
        yaxis=dict(
            # autorange=True,  # Enable autorange for y-axis
            range=yrange,
            fixedrange=True,  # VERY IMPORTANT TO OVERRIDE THE DEFAULT BEHAVIOR - allow y-axis zooming

            showgrid=True,
            gridcolor=colors['grid'],
            griddash='dot',
            gridwidth=1,

            tickformat=",.2f",
        ),
        margin=dict(l=20, r=20, t=40, b=20),
    )

    # add the initial trace (idk why, but this is needed to make the animation work)
    fig.add_trace(go.Candlestick(
        x=df_working['timestamp'][:1],
        open=df_working['open'][:1],
        close=df_working['close'][:1],
        high=df_working['high'][:1],
        low=df_working['low'][:1],
        name="Price",
        increasing={'line': {'color': colors['bullish_border'], 'width': 0.6}, 'fillcolor': colors['bullish_body']},
        decreasing={'line': {'color': colors['bearish_border'], 'width': 0.6}, 'fillcolor': colors['bearish_body']}
    ))

    # add the rest of the frames
    frames = []
    for i in range(0, 78):
        frame = go.Frame(
            data = [go.Candlestick(
                x=df_working['timestamp'][:i],
                open=df_working['open'][:i],
                close=df_working['close'][:i],
                high=df_working['high'][:i],
                low=df_working['low'][:i],
                name="Price",
                increasing={
                    'line': {'color': colors['bullish_border'], 'width': 0.6},
                    'fillcolor': colors['bullish_body']
                },
                
                decreasing={
                    'line': {'color': colors['bearish_border'], 'width': 0.6},
                    'fillcolor': colors['bearish_body']
                }
            )],
            name = f"Frame {i}"
        )
        frames.append(frame)
    fig.frames = frames

    fig.update_layout(
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            x=0.35, y=1.08,
            direction="right",
            buttons=[dict(
                label="▶",
                method="animate",
                args=[None, dict(frame=dict(duration=800, redraw=True), fromcurrent=True, mode="immediate", transition=dict(duration=0))]
            ),
            dict(
                label="▶▶",
                method="animate",
                args=[None, dict(frame=dict(duration=100, redraw=True), fromcurrent=True, mode="immediate", transition=dict(duration=0))]
            ),
            dict(
                label="⏸",
                method="animate",
                # the [None] in brackets is EXTREMELY IMPORTANT for some reason 
                # this is some deep deep undocumented shit
                # args=[None, ...]	Restarts from frame 0
                # args=[[None], ...]	Pauses but keeps current frame
                args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate", transition=dict(duration=0))]
            )]
        )]
    )

    fig.update_layout(
        sliders=[dict(
                y=-0.1,
                active=0,
                currentvalue=dict(prefix='Frame: '),
                steps=[dict(
                    args=[[f.name], dict(frame=dict(duration=800, redraw=True), mode='immediate')],
                    label=i,
                    method='animate'
                ) for i, f in enumerate(fig.frames)]
            )]
    )

    return fig

def add_entry_tp_sl(fig, entry, sl, tp):
    # remove any existing level lines
    fig.update_layout(shapes=[shape for shape in fig.layout.shapes if not shape.name or 'level' not in shape.name])
    
    fig.add_hrect(y0=sl, y1=entry, line_width=0, fillcolor="#FF6347", opacity=0.2, layer="below", name="sl_level")
    fig.add_hrect(y0=entry, y1=tp, line_width=0, fillcolor="#32CD32", opacity=0.2, layer="below", name="tp_level")

    return fig