from flask import Flask, redirect, request, session, render_template
from dotenv import load_dotenv
import os
import requests
from jose import jwt
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
REDIRECT_URI = os.getenv("ZOHO_REDIRECT_URI")
ZOHO_ACCOUNTS_URL = os.getenv("ZOHO_ACCOUNTS_URL")


@app.route('/')
def home():
    if 'user' in session:
        user = session['user']
        return f"""
        ✅ Already logged in!<br><br>
        Name: {user['name']}<br>
        Email: {user['email']}<br>
        Zoho User ID: {user['sub']}<br>
        <a href="/logout">Logout</a>
        """
    return render_template('login.html')


@app.route('/login')
def login():
    zoho_auth_url = (
        f"{ZOHO_ACCOUNTS_URL}/oauth/v2/auth?"
        f"client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&scope=openid email profile"
        f"&redirect_uri={REDIRECT_URI}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return redirect(zoho_auth_url)


@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "No code received from Zoho", 400

    # Exchange code for tokens
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

    if res.status_code != 200:
        return f"Failed to get token: {res.text}", 400

    tokens = res.json()
    id_token = tokens.get('id_token')
    if not id_token:
        return "No id_token received", 400

    # Decode id_token (JWT) — unverified for quick POC
    decoded = jwt.get_unverified_claims(id_token)

    session['user'] = {
        'email': decoded.get('email'),
        'sub': decoded.get('sub'),
        'name': decoded.get('name', 'No Name')
    }

    return redirect('/')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(port=8000, debug=True)
