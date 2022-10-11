import json, hmac, hashlib, time, base64, uuid, requests
from urllib.parse import urlparse
from keys import PORTFOLIO_ID, API_KEY, PASSPHRASE, SECRET_KEY

def prime_service_calls(app):

    headers = {
        'X-CB-ACCESS-SIGNATURE': signature_b64,
        'X-CB-ACCESS-timestamp': timestamp,
        'X-CB-ACCESS-KEY': API_KEY,
        'X-CB-ACCESS-PASSPHRASE': PASSPHRASE,
        'Accept': 'application/json'
    }