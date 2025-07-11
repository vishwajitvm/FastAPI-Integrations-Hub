import requests
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from jose import jwt
from starlette.config import Config

# Config setup (can also be read from .env)
config = Config(".env")

ZOHO_ACCOUNTS_URL = config("ZOHO_ACCOUNTS_URL")
CLIENT_ID = config("CLIENT_ID")
CLIENT_SECRET = config("CLIENT_SECRET")
REDIRECT_URI = config("REDIRECT_URI")

router = APIRouter()

# import requests
# from flask import current_app
# from jose import jwt

# def exchange_code_for_tokens(code):
#     token_url = f"{current_app.config['ZOHO_ACCOUNTS_URL']}/oauth/v2/token"
#     data = {
#         'client_id': current_app.config['CLIENT_ID'],
#         'client_secret': current_app.config['CLIENT_SECRET'],
#         'grant_type': 'authorization_code',
#         'code': code,
#         'redirect_uri': current_app.config['REDIRECT_URI'],
#     }
#     headers = {'Content-Type': 'application/x-www-form-urlencoded'}
#     res = requests.post(token_url, data=data, headers=headers)
#     return res



def exchange_code_for_tokens(code: str):
    token_url = f"{ZOHO_ACCOUNTS_URL}/oauth/v2/token"
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    res = requests.post(token_url, data=data, headers=headers)
    return res


@router.get("/oauth/callback")
async def oauth_callback(code: str):
    response = exchange_code_for_tokens(code)
    if response.ok:
        tokens = response.json()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        # You can optionally decode or store tokens here
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "message": "Token exchange successful"
        }
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to exchange code for tokens")

