from dash import Dash, html, dcc
from callbacks import register_callbacks
from prime_api import prime_calls

app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Coinbase Prime trading application'),
    html.Div(id='price-ref', style={'padding-top': 10, 'font-size': '22px'}),
    html.Div(id='portfolio-bal', style={'padding-top': 10, 'padding-bottom': 30, 'font-size': '22px'}),
    html.Div([
        dcc.Dropdown(['ETH-USD', 'BTC-USD', 'CRV-USD', 'SOL-USD', 'CBETH-USD', 'CBETH-ETH'],
                     'ETH-USD', id='product-switcher', style={'width': '150px'}),
        dcc.Dropdown(['1m', '5m', '15m', '1h', '6h', '1d'], '1h',
                     id='gran-switcher',
                     style={'width': '150px'})
    ]),

    dcc.Graph(id='product-chart', style={'width':'90%'}),
    html.H1(children='Buy/Sell'),
    html.Div(dcc.Input(id='amount-box', type='text')),
    dcc.Dropdown(['BUY', 'SELL'], 'BUY', id='buy-sell-toggle',style={'width': '150px'}),
    html.Button('Submit', id='submit-button', n_clicks=0),
    html.Div(id='buy-sell-response', style={'padding-top': 10})

], style={'padding': 30, 'flex': 1,'font-family': 'Inter'})

register_callbacks(app)
prime_calls(app)

if __name__ == '__main__':
    app.run_server(debug=True)
