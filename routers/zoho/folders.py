from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import requests
from config import Config
from routers.zoho.auth import user_sessions

router = APIRouter(prefix="/folders", tags=["Zoho Folders"])

@router.get("/my", response_class=HTMLResponse)
async def my_folders():
    user = user_sessions.get("current_user")
    if not user:
        return HTMLResponse("Not logged in", status_code=401)

    access_token = user['access_token']
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}

    user_url = f"{Config.ZOHO_API_URL}/workdrive/api/v1/users/me"
    res = requests.get(user_url, headers=headers)

    if res.status_code != 200:
        return HTMLResponse(f"Failed to fetch user details: {res.text}", status_code=400)

    user_data = res.json()
    root_folder_id = (
        user_data.get("data", {})
        .get("attributes", {})
        .get("root_folder_id")
    )

    if not root_folder_id:
        return HTMLResponse("Could not get My Folders root ID", status_code=400)

    files_url = f"{Config.ZOHO_API_URL}/workdrive/api/v1/folders/{root_folder_id}/files"
    res2 = requests.get(files_url, headers=headers)

    if res2.status_code == 200:
        files = res2.json()
        output = "<h3>My Folders & Files:</h3><ul>"
        for file in files.get("data", []):
            fname = file.get("attributes", {}).get("name", "Unnamed")
            ftype = file.get("type", "unknown")
            output += f"<li>{fname} — {ftype}</li>"
        output += "</ul><a href='/'>Back</a>"
        return HTMLResponse(output)
    else:
        return HTMLResponse(f"Failed to fetch files: {res2.text}", status_code=400)

@router.get("/team", response_class=HTMLResponse)
async def team_folders():
    user = user_sessions.get("current_user")
    if not user:
        return HTMLResponse("Not logged in", status_code=401)

    access_token = user['access_token']
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}

    teams_url = f"{Config.ZOHO_API_URL}/workdrive/api/v1/users/me/teams"
    res = requests.get(teams_url, headers=headers)

    if res.status_code != 200:
        return HTMLResponse(f"Failed to get teams: {res.text}", status_code=400)

    teams_data = res.json()
    output = "<h3>Team Folders & Files:</h3>"

    teams = teams_data.get("data", [])
    if not teams:
        return HTMLResponse("No teams found", status_code=400)

    for team in teams:
        team_id = team.get("id")
        team_name = team.get("attributes", {}).get("name", "Unnamed Team")
        output += f"<h4>Team: {team_name}</h4><ul>"

        teamfolders_url = f"{Config.ZOHO_API_URL}/workdrive/api/v1/teamfolders?org_id={team_id}"
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
    return HTMLResponse(output)
