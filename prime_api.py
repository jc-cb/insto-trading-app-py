import json
import hmac
import hashlib
import time
import base64
import uuid
import requests
from urllib.parse import urlparse
from dash import Input, Output, State
from keys import PORTFOLIO_ID, API_KEY, PASSPHRASE, SECRET_KEY

balanceEndpoint = f'https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/balances?balance_type=TRADING_BALANCES&symbols='
orderEndpoint = f'https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/order'

def make_prime_call(uri, method, body={}):
    timestamp = str(int(time.time()))
    url_path = urlparse(uri).path
    # need to update to handle if body
    if len(body) == 0:
        message = timestamp + method + url_path
    else:
        message = timestamp + method + url_path + json.dumps(body)

    signature = hmac.digest(SECRET_KEY.encode(
        'utf-8'), message.encode('utf-8'), hashlib.sha256)
    signature_b64 = base64.b64encode(signature)
    headers = {
        'X-CB-ACCESS-SIGNATURE': signature_b64,
        'X-CB-ACCESS-TIMESTAMP': timestamp,
        'X-CB-ACCESS-KEY': API_KEY,
        'X-CB-ACCESS-PASSPHRASE': PASSPHRASE,
        'Accept': 'application/json'
    }

    if method == 'POST':
        response = requests.post(uri, headers=headers, json=body)
    else:
        response = requests.get(uri, headers=headers)
    parsed = json.loads(response.text)
    return parsed


def make_balance_call(asset):
    uri = f'{balanceEndpoint}{asset}'
    return make_prime_call(uri, 'GET')


def make_order_call(amount, buysell, asset):
    client_order_id = uuid.uuid4()

    payload = {
        'portfolio_id': PORTFOLIO_ID,
        'product_id': asset,
        'client_order_id': str(client_order_id),
        'side': buysell,
        'type': 'MARKET',
        'base_quantity': amount
    }
    parsed_response = make_prime_call(orderEndpoint, 'POST', payload)
    return parsed_response


def prime_calls(app):
    @app.callback(
        Output('portfolio-bal', 'children'),
        Input('product-switcher', 'value'))
    def update_balance(product_selection):
        time.sleep(0.5)
        pair1 = product_selection.split('-')[0]
        pair2 = product_selection.split('-')[1]

        newBal1 = make_balance_call(pair1)
        balance1 = newBal1['balances'][0]['amount']
        if pair1 == 'USD':
            balance1 = '$'+balance1[:6]

        newBal2 = make_balance_call(pair2)
        balance2 = newBal2['balances'][0]['amount']
        if pair2 == 'USD':
            balance2 = '$'+balance2[:6]
        return f'Your {pair1} balance is {balance1}. Your {pair2} balance is {balance2}.'

    @app.callback(
        Output('buy-sell-response', 'children'),
        State('amount-box', 'value'),
        State('buy-sell-toggle', 'value'),
        State('product-switcher', 'value'),
        Input('submit-button', 'n_clicks'))
    def update_buysell(amount, buysell, asset, n_clicks):
        if n_clicks:
            parsed_response = make_order_call(amount, buysell, asset)
            return json.dumps(parsed_response, indent=3)