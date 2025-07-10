from flask import Blueprint, redirect, request, session, url_for, render_template, current_app
from utils.zoho_client import exchange_code_for_tokens
from jose import jwt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    if 'user' in session:
        user = session['user']
        return f"""
        ✅ Logged in!<br><br>
        Name: {user['name']}<br>
        Email: {user['email']}<br>
        Zoho User ID: {user['sub']}<br><br>
        <a href="/folders/my_folders">List My Folders & Files</a><br>
        <a href="/folders/list_team_folders">List Team Folders & Files</a><br>
        <a href="/logout">Logout</a>
        """
    return render_template('login.html')

@auth_bp.route('/login')
def login():
    url = (
        f"{current_app.config['ZOHO_ACCOUNTS_URL']}/oauth/v2/auth?"
        f"scope=WorkDrive.files.ALL,WorkDrive.teamfolders.READ,openid,email,profile"
        f"&client_id={current_app.config['CLIENT_ID']}"
        f"&response_type=code"
        f"&access_type=offline"
        f"&redirect_uri={current_app.config['REDIRECT_URI']}"
        f"&prompt=consent"
    )
    return redirect(url)

@auth_bp.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "No code received", 400

    res = exchange_code_for_tokens(code)

    if res.status_code != 200:
        return f"Failed to get token: {res.text}", 400

    tokens = res.json()
    id_token = tokens.get('id_token')
    access_token = tokens.get('access_token')

    if not access_token:
        return "No access_token received", 400

    user_info = {
        'access_token': access_token,
    }

    if id_token:
        decoded = jwt.get_unverified_claims(id_token)
        user_info['email'] = decoded.get('email', 'No email')
        user_info['sub'] = decoded.get('sub', 'No sub')
        user_info['name'] = decoded.get('name', 'No Name')
    else:
        user_info['email'] = 'No email'
        user_info['sub'] = 'No sub'
        user_info['name'] = 'No Name'

    session['user'] = user_info

    return redirect(url_for('auth.home'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.home'))
