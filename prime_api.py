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
import json
import hmac
import hashlib
import time
import base64
import uuid
import os
import requests
from urllib.parse import urlparse
from dash import Input, Output, State, ctx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("API_KEY")
SECRET_KEY = os.environ.get("SECRET_KEY")
PASSPHRASE = os.environ.get("PASSPHRASE")
PORTFOLIO_ID = os.environ.get("PORTFOLIO_ID")

balanceEndpoint = f"https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/balances?balance_type=TRADING_BALANCES&symbols="
orderEndpoint = f"https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/order"
getOrderEndpoint = f"https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/orders/"


def make_prime_call(uri, method, body={}):
    """
    make_prime_call generates and submits requests to Coinbase Prime API
    """
    timestamp = str(int(time.time()))
    url_path = urlparse(uri).path

    if len(body) == 0:
        message = timestamp + method + url_path
    else:
        message = timestamp + method + url_path + json.dumps(body)

    signature = hmac.digest(
        SECRET_KEY.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
    )
    signature_b64 = base64.b64encode(signature)
    headers = {
        "X-CB-ACCESS-SIGNATURE": signature_b64,
        "X-CB-ACCESS-TIMESTAMP": timestamp,
        "X-CB-ACCESS-KEY": API_KEY,
        "X-CB-ACCESS-PASSPHRASE": PASSPHRASE,
        "Accept": "application/json",
    }

    if method == "POST":
        response = requests.post(uri, headers=headers, json=body)
    else:
        response = requests.get(uri, headers=headers)
    parsed = json.loads(response.text)
    return parsed


def make_balance_call(asset):
    """
    make_balance_call generates and places balance request using make_prime_call
    """
    uri = f"{balanceEndpoint}{asset}"
    return make_prime_call(uri, "GET")


def make_get_order_call(order_id):
    """
    make_get_order_call returns order details following order placement
    """
    uri = f"{getOrderEndpoint}{order_id}"
    return make_prime_call(uri, "GET")


def make_order_call(amount, buysell, asset):
    """
    make_order_call generates orders payload to be used by make_prime_call
    """
    client_order_id = uuid.uuid4()

    payload = {
        "portfolio_id": PORTFOLIO_ID,
        "product_id": asset,
        "client_order_id": str(client_order_id),
        "side": buysell,
        "type": "MARKET",
        "base_quantity": amount,
    }
    parsed_response = make_prime_call(orderEndpoint, "POST", payload)
    if parsed_response['message']:
        return f"error: {parsed_response}"
    else:
        order_id = parsed_response["order_id"]

        order_details = make_get_order_call(order_id)
        order_details = order_details["order"]

        order_get_id = order_details["id"]
        order_get_product = order_details["product_id"]
        order_get_side = order_details["side"]
        order_get_qty = order_details["base_quantity"]

        return f"Order details: {order_get_product} {order_get_side} {order_get_qty}. Order ID: {order_get_id}"


def generate_new_balance(product_selection):
    pair1 = product_selection.split("-")[0]
    pair2 = product_selection.split("-")[1]
    newbal1 = make_balance_call(pair1)
    balance1 = newbal1["balances"][0]["amount"]
    if pair1 == "USD":
        balance1 = "$" + balance1[:6]

    newbal2 = make_balance_call(pair2)
    balance2 = newbal2["balances"][0]["amount"]
    if pair2 == "USD":
        balance2 = "$" + balance2[:6]

    return f"Your {pair1} balance is {balance1}. Your {pair2} balance is {balance2}."


def prime_calls(app):
    """
    prime_calls orchestrates balance refreshes and order placement
    """

    @app.callback(
        [Output("buy-sell-response", "children"), Output("amount-box", "value")],
        State("amount-box", "value"),
        State("buy-sell-toggle", "value"),
        State("product-switcher", "value"),
        Input("submit-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def update_buysell(amount, buysell, asset, n_clicks):
        """
        update_buysell clears purchase quantity after order placement
        """
        if n_clicks:
            order_response = make_order_call(amount, buysell, asset)
            return order_response, ""

    @app.callback(
        Output("portfolio-bal", "children"),
        Input("product-switcher", "value"),
        Input("portfolio-bal", "children"),
        Input("submit-button", "n_clicks"),
    )
    def update_balance(product_selection, portfolio_bal, n_clicks):
        """
        update_balance refreshes account balances following order placement
        """
        balances = generate_new_balance(product_selection)

        i = 0
        if portfolio_bal is not None:
            while i < 3:
                bal = balances.split(". Your")[0]
                ref = portfolio_bal.split(". Your")[0]
                if bal == ref:
                    time.sleep(0.2)
                    balances = generate_new_balance(product_selection)
                    i = i + 1
                    bal = balances.split(". Your")[0]
                else:
                    break

        return balances
