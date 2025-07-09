from flask import Flask, redirect, request, session, render_template, url_for
import os
import requests
from dotenv import load_dotenv
from jose import jwt
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
REDIRECT_URI = os.getenv("ZOHO_REDIRECT_URI")
ZOHO_ACCOUNTS_URL = "https://accounts.zoho.com"
ZOHO_API_URL = "https://www.zohoapis.com"

@app.route('/')
def home():
    if 'user' in session:
        user = session['user']
        return f"""
        ✅ Logged in!<br><br>
        Name: {user['name']}<br>
        Email: {user['email']}<br>
        Zoho User ID: {user['sub']}<br><br>
        <a href="/team_folders">List Team Folders</a><br>
        <a href="/logout">Logout</a>
        """
    return render_template('login.html')


@app.route('/login')
def login():
    zoho_auth_url = (
        f"{ZOHO_ACCOUNTS_URL}/oauth/v2/auth?"
        f"scope=WorkDrive.files.ALL,openid,email,profile"
        f"&client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&access_type=offline"
        f"&redirect_uri={REDIRECT_URI}"
        f"&prompt=consent"
    )
    return redirect(zoho_auth_url)


@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "No code received from Zoho", 400

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

    return redirect(url_for('home'))


@app.route('/team_folders')
def team_folders():
    if 'user' not in session:
        return redirect('/')

    access_token = session['user']['access_token']
    api_url = f"{ZOHO_API_URL}/workdrive/api/v1/teamfolders"

    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}"
    }

    res = requests.get(api_url, headers=headers)

    if res.status_code == 200:
        folders = res.json()
        output = "<h3>Team Folders:</h3><ul>"
        for folder in folders.get("data", []):
            name = folder.get("attributes", {}).get("name", "Unnamed")
            folder_id = folder.get("id")
            output += f'<li>{name} — <a href="/list_files/{folder_id}">List Files</a></li>'
        output += "</ul><a href='/'>Back</a>"
        return output
    else:
        return f"Failed to fetch team folders: {res.text}", 400


@app.route('/list_files/<folder_id>')
def list_files(folder_id):
    if 'user' not in session:
        return redirect('/')

    access_token = session['user']['access_token']
    api_url = f"{ZOHO_API_URL}/workdrive/api/v1/folders/{folder_id}/files"

    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}"
    }

    res = requests.get(api_url, headers=headers)

    if res.status_code == 200:
        files = res.json()
        output = f"<h3>Files in Folder {folder_id}:</h3><ul>"
        for file in files.get("data", []):
            fname = file.get("attributes", {}).get("name", "Unnamed")
            output += f"<li>{fname}</li>"
        output += "</ul><a href='/team_folders'>Back to Folders</a>"
        return output
    else:
        return f"Failed to fetch files: {res.text}", 400


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(port=8000, debug=True)
