import requests
from flask import current_app
from jose import jwt

def exchange_code_for_tokens(code):
    token_url = f"{current_app.config['ZOHO_ACCOUNTS_URL']}/oauth/v2/token"
    data = {
        'client_id': current_app.config['CLIENT_ID'],
        'client_secret': current_app.config['CLIENT_SECRET'],
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': current_app.config['REDIRECT_URI'],
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    res = requests.post(token_url, data=data, headers=headers)
    return res
