"""
Copyright 2022 Coinbase Global, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import json, requests
from dash import Input, Output
from datetime import datetime


def register_price(app):
    """
    register_price functionalizes price callbacks into app.py
    """

    @app.callback(
        Output("price-ref", "children"),
        Input("product-switcher", "value"))
    def update_price(product_selection):
        """
        update_price calls Exchange Get Product Ticker endpoint for price data
        """
        product_id = product_selection
        denomination = product_id[-3:]

        now = datetime.now().strftime("%H:%M:%S")
        if "06:00:00" < now < "12:00:00":
            now = "Good morning"
        elif now < "18:00:00":
            now = "Good afternoon"
        else:
            now = "Good evening"

        url = f"https://api.exchange.coinbase.com/products/{product_id}/ticker"
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers)
        parse = json.loads(response.text)
        price_val = parse["price"]

        return f"{now}. The price of {product_id} is {price_val} {denomination}."
