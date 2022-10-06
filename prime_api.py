import json, hmac, hashlib, time, base64, uuid, requests
from urllib.parse import urlparse
from dash import Input, Output, State
from keys import PORTFOLIO_ID, API_KEY, PASSPHRASE, SECRET_KEY

def prime_calls(app):
    @app.callback(
        Output('portfolio-bal', 'children'),
        Input('product-switcher', 'value'),
        Input('submit-button', 'n_clicks'))
    def update_balance(product_selection,n_clicks):
        time.sleep(0.5)
        balances = list()
        assets = list()
        timestamp = str(int(time.time()))
        for i in range(2):
            product = product_selection.split('-')[i]
            uri = f'https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/balances?symbols={product}&balance_type=TRADING_BALANCES'
            METHOD = 'GET'
            url_path = urlparse(uri).path
            message = timestamp + METHOD + url_path
            signature = hmac.digest(SECRET_KEY.encode('utf-8'), message.encode('utf-8'), hashlib.sha256)
            signature_b64 = base64.b64encode(signature)

            headers = {
                'X-CB-ACCESS-SIGNATURE': signature_b64,
                'X-CB-ACCESS-timestamp': timestamp,
                'X-CB-ACCESS-KEY': API_KEY,
                'X-CB-ACCESS-PASSPHRASE': PASSPHRASE,
                'Accept': 'application/json'
            }

            response = requests.get(uri, headers=headers)
            parsed_response = json.loads(response.text)
            balance = parsed_response['balances'][0]['amount']
            if product == 'USD':
                balance = '$'+balance[:6]
            assets.append(product)
            balances.append(balance)

        return f'Your {assets[0]} balance is {balances[0]}. Your {assets[1]} balance is {balances[1]}.'

    @app.callback(
        Output('buy-sell-response', 'children'),
        State('amount-box', 'value'),
        State('buy-sell-toggle', 'value'),
        State('product-switcher', 'value'),
        Input('submit-button', 'n_clicks'))
    def update_buysell(amount,buysell,asset,n_clicks):
        if n_clicks:
            uri = f'https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/order'
            timestamp = str(int(time.time()))
            client_order_id = uuid.uuid4()
            method = 'POST'
            product_id = asset
            side = buysell
            order_type = 'MARKET'
            base_quantity = amount

            payload = {
                'portfolio_id': PORTFOLIO_ID,
                'product_id': product_id,
                'client_order_id': str(client_order_id),
                'side': side,
                'type': order_type,
                'base_quantity': base_quantity
            }

            url_path = urlparse(uri).path
            message = timestamp + method + url_path + json.dumps(payload)
            signature = hmac.new(SECRET_KEY.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).digest()
            signature_b64 = base64.b64encode(signature)

            headers = {
                'X-CB-ACCESS-SIGNATURE': signature_b64,
                'X-CB-ACCESS-timestamp': timestamp,
                'X-CB-ACCESS-KEY': API_KEY,
                'X-CB-ACCESS-PASSPHRASE': PASSPHRASE,
                'Accept': 'application/json'
            }

            response = requests.post(uri, json=payload, headers=headers)
            parsed_response = json.loads(response.text)

            return json.dumps(parsed_response, indent=3)
