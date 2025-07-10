# blueprints/zoho/folders.py

from flask import Blueprint, session, redirect
from .zoho_client import get_user_root_folder_id, list_files_in_folder, get_teams_and_teamfolders

zoho_folders_bp = Blueprint('zoho_folders', __name__, url_prefix='/zoho/folders')

@zoho_folders_bp.route('/my_folders')
def my_folders():
    if 'user' not in session:
        return redirect('/')

    access_token = session['user']['access_token']

    root_folder_id = get_user_root_folder_id(access_token)
    if not root_folder_id:
        return "Could not get My Folders root ID", 400

    files = list_files_in_folder(access_token, root_folder_id)
    output = f"<h3>My Folders & Files:</h3><ul>"
    for file in files.get("data", []):
        fname = file.get("attributes", {}).get("name", "Unnamed")
        ftype = file.get("type", "unknown")
        output += f"<li>{fname} — {ftype}</li>"
    output += "</ul><a href='/'>Back</a>"
    return output


@zoho_folders_bp.route('/team_folders')
def team_folders():
    if 'user' not in session:
        return redirect('/')

    access_token = session['user']['access_token']

    teams = get_teams_and_teamfolders(access_token)
    if not teams:
        return "No teams found or failed to fetch", 400

    output = "<h3>Team Folders & Files:</h3>"
    for team_name, folders in teams.items():
        output += f"<h4>Team: {team_name}</h4><ul>"
        for folder in folders:
            folder_name = folder.get("attributes", {}).get("name", "Unnamed Folder")
            folder_id = folder.get("id", "No ID")
            output += f"<li>{folder_name} (ID: {folder_id})</li>"
        output += "</ul>"

    output += "<a href='/'>Back</a>"
    return output
