import json, requests
import plotly.graph_objects as go
import pandas as pd
from dash import Input, Output
from ta import momentum
from ta.trend import MACD
from plotly.subplots import make_subplots


def create_dataframe(parse):
    """
    create_dataframe is a function called by register_graph to build a dataframe from Coinbase candlestick chart data

    diff = used to color label volume candles based on timeframe performance
    rsi = relative strength index set to 14 unit window
    MA20 / MA7 = simple moving average calculated using close price for 20 and 7 unit windows
    """
    df = pd.DataFrame(parse,
                      columns=['timestamp', 'price_low', 'price_high', 'price_open', 'price_close', 'volume'])
    df = df.loc[::-1].reset_index(drop=True)
    df['diff'] = df['price_close'] - df['price_open']
    df['rsi'] = momentum.rsi(df["price_close"], window=14, fillna=False)
    df.loc[df['diff'] >= 0, 'color'] = 'green'
    df.loc[df['diff'] < 0, 'color'] = 'red'
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df['rsi'] = momentum.rsi(df['price_close'], window=14, fillna=False)
    df['MA20'] = df['price_close'].rolling(window=20).mean()
    df['MA7'] = df['price_close'].rolling(window=7).mean()
    return df

def register_graph(app):
    """
    register_graph updates Plotly graph using dataframe built by create_dataframe on UI switch of product or granularity

    macd = moving average convergence divergence calculated using 26/12/9 unit windows
    """
    @app.callback(
        Output('product-chart', 'figure'),
        Input('product-switcher', 'value'),
        Input('gran-switcher', 'value'))
    def update_output(product_selection, granularity_selection):
        product_id = product_selection
        granularity = granularity_selection
        url = f'https://api.exchange.coinbase.com/products/{product_id}/candles?granularity={str(granularity)}'
        headers = {
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers)
        parse = json.loads(response.text)

        df = create_dataframe(parse)
        max_volume = df['volume'].max()

        macd = MACD(close=df['price_close'],
                    window_slow=26,
                    window_fast=12,
                    window_sign=9)

        fig1 = make_subplots(rows=3, cols=1, shared_xaxes=True,
                             vertical_spacing=0.01,
                             row_heights=[0.8, 0.2, 0.15],
                             specs=[[{"secondary_y": True}],[{"secondary_y": True}],[{"secondary_y": True}]]
                             )
        fig1.add_trace(go.Candlestick(x=df['timestamp'],
                                     open=df['price_open'],
                                     high=df['price_high'],
                                     low=df['price_low'],
                                     close=df['price_close'],
                                     name='Price'))
        fig1.add_trace(go.Scatter(x=df['timestamp'],
                                 y=df['MA20'],
                                 opacity=0.7,
                                 line=dict(color='blue', width=2),
                                 name='MA 20'))
        fig1.add_trace(go.Scatter(x=df['timestamp'],
                                 y=df['MA7'],
                                 opacity=0.7,
                                 line=dict(color='orange', width=2),
                                 name='MA 7'))
        fig1.add_trace(go.Bar(x=df['timestamp'],
                              y=df['volume'],
                              name='Volume',
                              marker={'color': df['color']}),
                                secondary_y=True)
        fig1.add_trace(go.Bar(x=df['timestamp'],
                             y=macd.macd_diff()
                             ), row=2, col=1)
        fig1.add_trace(go.Scatter(x=df['timestamp'],
                                 y=macd.macd(),
                                 line=dict(color='black', width=2)
                                 ), row=2, col=1)
        fig1.add_trace(go.Scatter(x=df['timestamp'],
                                 y=macd.macd_signal(),
                                 line=dict(color='red', width=1)
                                 ), row=2, col=1)
        fig1.add_trace(go.Scatter(x=df['timestamp'],
                                 y=df['rsi'],
                                 mode="lines",
                                 line=dict(color='purple', width=1)),
                                 row=3, col=1)

        fig1.update_layout(height=900,
                           showlegend=False,
                           xaxis_rangeslider_visible=False)

        fig1.update_yaxes(title_text="<b>Price</b>", row=1, col=1)
        fig1.update_yaxes(title_text="<b>Volume</b>", range=[0, max_volume * 5], row=1, col=1, secondary_y=True)
        fig1.update_yaxes(title_text="<b>MACD</b>", showgrid=False, row=2, col=1)
        fig1.update_yaxes(title_text="<b>RSI</b>", row=3, col=1)
        return fig1
