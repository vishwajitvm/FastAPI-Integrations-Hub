from flask import Flask, redirect, request, session, render_template, url_for
import os
import requests
from dotenv import load_dotenv
from jose import jwt
import json


# Load .env
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
        <a href="/my_folders">List My Folders & Files</a><br>
        <a href="/list_team_folders">List Team Folders & Files</a><br>
        <a href="/logout">Logout</a>
        """
    return render_template('login.html')


@app.route('/login')
def login():
    zoho_auth_url = (
        f"{ZOHO_ACCOUNTS_URL}/oauth/v2/auth?"
        f"scope=WorkDrive.files.ALL,WorkDrive.teamfolders.READ,openid,email,profile"
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


@app.route('/my_folders')
def my_folders():
    if 'user' not in session:
        return redirect('/')

    access_token = session['user']['access_token']

    # Step 1: Get user details to get My Folders root ID
    user_url = f"{ZOHO_API_URL}/workdrive/api/v1/users/me"
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}"
    }

    res = requests.get(user_url, headers=headers)

    if res.status_code != 200:
        return f"Failed to fetch user details: {res.text}", 400

    user_data = res.json()
    # print(user_data)  # Debugging: Check structure
    print(json.dumps(user_data, indent=4))


    # Updated: safer access to root_folder_id
    root_folder_id = (
        user_data.get("data", {})
        .get("attributes", {})
        .get("root_folder_id")
    )

    if not root_folder_id:
        return "Could not get My Folders root ID", 400

    # Step 2: List files in My Folders root
    files_url = f"{ZOHO_API_URL}/workdrive/api/v1/folders/{root_folder_id}/files"

    res2 = requests.get(files_url, headers=headers)

    if res2.status_code == 200:
        files = res2.json()
        output = f"<h3>My Folders & Files:</h3><ul>"
        for file in files.get("data", []):
            fname = file.get("attributes", {}).get("name", "Unnamed")
            ftype = file.get("type", "unknown")
            output += f"<li>{fname} — {ftype}</li>"
        output += "</ul><a href='/'>Back</a>"
        return output
    else:
        return f"Failed to fetch files: {res2.text}", 400


@app.route('/list_team_folders')
def list_team_folders():
    if 'user' not in session:
        return redirect('/')

    access_token = session['user']['access_token']
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}"
    }

    # Get list of teams
    teams_url = f"{ZOHO_API_URL}/workdrive/api/v1/users/me/teams"
    res = requests.get(teams_url, headers=headers)

    if res.status_code != 200:
        return f"Failed to get teams: {res.text}", 400

    teams_data = res.json()
    output = "<h3>Team Folders & Files:</h3>"

    teams = teams_data.get("data", [])
    if not teams:
        return "No teams found", 400

    for team in teams:
        team_id = team.get("id")
        team_name = team.get("attributes", {}).get("name", "Unnamed Team")
        output += f"<h4>Team: {team_name}</h4><ul>"

        # Get team folders for each team
        teamfolders_url = f"{ZOHO_API_URL}/workdrive/api/v1/teamfolders?org_id={team_id}"
        res2 = requests.get(teamfolders_url, headers=headers)

        if res2.status_code != 200:
            output += f"<li>Failed to list folders for {team_name}: {res2.text}</li>"
            continue

        folders_data = res2.json()
        for folder in folders_data.get("data", []):
            folder_name = folder.get("attributes", {}).get("name", "Unnamed Folder")
            folder_id = folder.get("id", "No ID")
            output += f"<li>{folder_name} (ID: {folder_id})</li>"

        output += "</ul>"

    output += "<a href='/'>Back</a>"
    return output


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(port=8000, debug=True)
