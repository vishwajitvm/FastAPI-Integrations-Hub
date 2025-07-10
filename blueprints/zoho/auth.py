# blueprints/zoho/auth.py

from flask import Blueprint, redirect, request, session, url_for, render_template
from jose import jwt
from .zoho_client import exchange_code_for_tokens, decode_id_token

zoho_auth_bp = Blueprint('zoho_auth', __name__)

@zoho_auth_bp.route('/')
def home():
    if 'user' in session:
        user = session['user']
        return f"""
        ✅ Logged in!<br><br>
        Name: {user['name']}<br>
        Email: {user['email']}<br>
        Zoho User ID: {user['sub']}<br><br>
        <a href="/zoho/folders/my_folders">List My Folders & Files</a><br>
        <a href="/zoho/folders/team_folders">List Team Folders & Files</a><br>
        <a href="/logout">Logout</a>
        """
    return render_template('login.html')


@zoho_auth_bp.route('/login')
def login():
    from config import Config

    zoho_auth_url = (
        f"{Config.ZOHO_ACCOUNTS_URL}/oauth/v2/auth?"
        f"scope=WorkDrive.files.ALL,WorkDrive.teamfolders.READ,openid,email,profile"
        f"&client_id={Config.CLIENT_ID}"
        f"&response_type=code"
        f"&access_type=offline"
        f"&redirect_uri={Config.REDIRECT_URI}"
        f"&prompt=consent"
    )
    return redirect(zoho_auth_url)


@zoho_auth_bp.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "No code received from Zoho", 400

    tokens = exchange_code_for_tokens(code)
    if not tokens or 'access_token' not in tokens:
        return "Failed to get access token", 400

    id_token = tokens.get('id_token')
    user_info = {'access_token': tokens['access_token']}

    if id_token:
        decoded = decode_id_token(id_token)
        user_info.update({
            'email': decoded.get('email', 'No email'),
            'sub': decoded.get('sub', 'No sub'),
            'name': decoded.get('name', 'No name')
        })
    else:
        user_info.update({'email': 'No email', 'sub': 'No sub', 'name': 'No name'})

    session['user'] = user_info
    return redirect(url_for('zoho_auth.home'))


@zoho_auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')
