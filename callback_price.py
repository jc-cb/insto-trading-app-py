import json, requests
from dash import Input, Output
from datetime import datetime


def register_price(app):
    @app.callback(
        Output('price-ref', 'children'),
        Input('product-switcher', 'value'))
    def update_price(product_selection):
        product_id = product_selection
        denomination = product_id[-3:]

        now = datetime.now().strftime('%H:%M:%S')
        if '06:00:00' < now < '12:00:00':
            now = 'Good morning'
        elif now < '18:00:00':
            now = 'Good afternoon'
        else:
            now = 'Good evening'

        url = f'https://api.exchange.coinbase.com/products/{product_id}/ticker'
        headers = {
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers)
        parse = json.loads(response.text)
        price_val = parse['price']

        return f'{now}. The price of {product_id} is {price_val} {denomination}.'
