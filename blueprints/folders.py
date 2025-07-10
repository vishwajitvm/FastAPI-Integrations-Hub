from flask import Blueprint, session, redirect, current_app
import requests
import json

folders_bp = Blueprint('folders', __name__, url_prefix='/folders')

@folders_bp.route('/my_folders')
def my_folders():
    if 'user' not in session:
        return redirect('/')

    access_token = session['user']['access_token']
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}

    user_url = f"{current_app.config['ZOHO_API_URL']}/workdrive/api/v1/users/me"
    res = requests.get(user_url, headers=headers)

    if res.status_code != 200:
        return f"Failed to fetch user details: {res.text}", 400

    user_data = res.json()
    root_folder_id = (
        user_data.get("data", {})
        .get("attributes", {})
        .get("root_folder_id")
    )

    if not root_folder_id:
        return "Could not get My Folders root ID", 400

    files_url = f"{current_app.config['ZOHO_API_URL']}/workdrive/api/v1/folders/{root_folder_id}/files"
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

@folders_bp.route('/list_team_folders')
def list_team_folders():
    if 'user' not in session:
        return redirect('/')

    access_token = session['user']['access_token']
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}

    teams_url = f"{current_app.config['ZOHO_API_URL']}/workdrive/api/v1/users/me/teams"
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

        teamfolders_url = f"{current_app.config['ZOHO_API_URL']}/workdrive/api/v1/teamfolders?org_id={team_id}"
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
