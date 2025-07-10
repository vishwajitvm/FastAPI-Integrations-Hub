# blueprints/zoho/zoho_client.py

import requests
from jose import jwt
from config import Config

def exchange_code_for_tokens(code):
    token_url = f"{Config.ZOHO_ACCOUNTS_URL}/oauth/v2/token"
    data = {
        'client_id': Config.CLIENT_ID,
        'client_secret': Config.CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': Config.REDIRECT_URI,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    res = requests.post(token_url, data=data, headers=headers)
    if res.status_code == 200:
        return res.json()
    return None

def decode_id_token(id_token):
    try:
        return jwt.get_unverified_claims(id_token)
    except Exception as e:
        print(f"Failed to decode ID token: {e}")
        return {}

def get_user_root_folder_id(access_token):
    url = f"{Config.ZOHO_API_URL}/workdrive/api/v1/users/me"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"Failed to fetch user details: {res.text}")
        return None
    user_data = res.json()
    return user_data.get("data", {}).get("attributes", {}).get("root_folder_id")

def list_files_in_folder(access_token, folder_id):
    url = f"{Config.ZOHO_API_URL}/workdrive/api/v1/folders/{folder_id}/files"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json()
    print(f"Failed to fetch files: {res.text}")
    return {}

def get_teams_and_teamfolders(access_token):
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    teams_url = f"{Config.ZOHO_API_URL}/workdrive/api/v1/users/me/teams"
    res = requests.get(teams_url, headers=headers)
    if res.status_code != 200:
        print(f"Failed to get teams: {res.text}")
        return {}

    teams_data = res.json()
    teams_info = {}
    for team in teams_data.get("data", []):
        team_id = team.get("id")
        team_name = team.get("attributes", {}).get("name", "Unnamed Team")

        teamfolders_url = f"{Config.ZOHO_API_URL}/workdrive/api/v1/teamfolders?org_id={team_id}"
        res2 = requests.get(teamfolders_url, headers=headers)
        if res2.status_code != 200:
            print(f"Failed to list folders for {team_name}: {res2.text}")
            continue

        folders_data = res2.json()
        teams_info[team_name] = folders_data.get("data", [])

    return teams_info
