import json
from fastapi import APIRouter, Header, Query
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
import requests
from config import Config
from routers.zoho.auth import user_sessions
import html
from constants import response_messages as msg
from constants import status_codes as sc
from typing import Optional
from utils.shared import get_user_tokens
from utils.zoho_folder_helpers import get_folder_contents_json, collect_all_files_flat


router = APIRouter(prefix="/folders", tags=["Zoho Folders"])

@router.get("api/my-folder", response_class=JSONResponse)
async def my_folders():
    user = user_sessions.get("current_user")
    if not user:
        return JSONResponse({"error": msg.NOT_LOGGED_IN}, status_code=sc.HTTP_UNAUTHORIZED)

    access_token = user['access_token']
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}

    # Fetch user details
    user_url = f"{Config.ZOHO_API_URL}/workdrive/api/v1/users/me"
    res = requests.get(user_url, headers=headers)

    if res.status_code != sc.HTTP_OK:
        return JSONResponse({"error": f"{msg.FETCH_USER_FAILED}: {res.text}"}, status_code=sc.HTTP_BAD_REQUEST)

    user_data = res.json()

    # Get incomingfolders.related link
    incoming_folders_link = (
        user_data
        .get("data", {})
        .get("relationships", {})
        .get("incomingfolders", {})
        .get("links", {})
        .get("related")
    )

    if not incoming_folders_link:
        return JSONResponse({"error": msg.NO_ROOT_FOLDER}, status_code=sc.HTTP_BAD_REQUEST)

    # Fetch incoming folders
    res2 = requests.get(incoming_folders_link, headers=headers)
    if res2.status_code != sc.HTTP_OK:
        return JSONResponse({"error": f"{msg.FOLDERS_FETCH_FAILED}: {res2.text}"}, status_code=sc.HTTP_BAD_REQUEST)

    folders_data = res2.json()
    result = []

    for folder in folders_data.get("data", []):
        folder_json = get_folder_contents_json(folder, headers)
        result.append(folder_json)

    return JSONResponse(result, status_code=sc.HTTP_OK)

@router.get("api/my-teams", response_class=HTMLResponse)
async def team_folders():
    user = user_sessions.get("current_user")
    if not user:
        return HTMLResponse(msg.NOT_LOGGED_IN, status_code=sc.HTTP_UNAUTHORIZED)

    access_token = user['access_token']
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}

    teams_url = f"{Config.ZOHO_API_URL}/workdrive/api/v1/users/me/teams"
    res = requests.get(teams_url, headers=headers)

    if res.status_code != sc.HTTP_OK:
        return HTMLResponse(f"{msg.FOLDERS_FETCH_FAILED}: {res.text}", status_code=sc.HTTP_BAD_REQUEST)

    teams_data = res.json()
    output = "<h3>Team Folders & Files:</h3>"

    teams = teams_data.get("data", [])
    if not teams:
        return HTMLResponse(msg.NO_TEAMS_FOUND, status_code=sc.HTTP_BAD_REQUEST)

    for team in teams:
        team_id = team.get("id")
        team_name = team.get("attributes", {}).get("name", "Unnamed Team")
        output += f"<h4>Team: {team_name}</h4><ul>"

        teamfolders_url = f"{Config.ZOHO_API_URL}/workdrive/api/v1/teamfolders?org_id={team_id}"
        res2 = requests.get(teamfolders_url, headers=headers)

        if res2.status_code != sc.HTTP_OK:
            output += f"<li>{msg.FOLDERS_FETCH_FAILED} for {team_name}: {res2.text}</li>"
            continue

        folders_data = res2.json()
        for folder in folders_data.get("data", []):
            folder_name = folder.get("attributes", {}).get("name", "Unnamed Folder")
            folder_id = folder.get("id", "No ID")
            output += f"<li>{folder_name} (ID: {folder_id})</li>"

        output += "</ul>"

    output += "<a href='/'>Back</a>"
    return HTMLResponse(output, status_code=sc.HTTP_OK)

@router.get("api/my-folder-n8n", response_class=JSONResponse)
async def my_folders_n8n(user_id: str = Query(...)):
    # Get tokens synchronously
    tokens = get_user_tokens(user_id)
    if not tokens or not tokens.get("access_token"):
        return JSONResponse({"error": "User not logged in or token missing"}, status_code=sc.HTTP_UNAUTHORIZED)

    access_token = tokens["access_token"]
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}

    # Fetch user details
    user_url = f"{Config.ZOHO_API_URL}/workdrive/api/v1/users/me"
    res = requests.get(user_url, headers=headers)

    if res.status_code != sc.HTTP_OK:
        return JSONResponse({"error": f"{msg.FETCH_USER_FAILED}: {res.text}"}, status_code=sc.HTTP_BAD_REQUEST)

    user_data = res.json()

    # Get incoming folders link
    incoming_folders_link = (
        user_data
        .get("data", {})
        .get("relationships", {})
        .get("incomingfolders", {})
        .get("links", {})
        .get("related")
    )

    if not incoming_folders_link:
        return JSONResponse({"error": msg.NO_ROOT_FOLDER}, status_code=sc.HTTP_BAD_REQUEST)

    # Fetch folders
    res2 = requests.get(incoming_folders_link, headers=headers)
    if res2.status_code != sc.HTTP_OK:
        return JSONResponse({"error": f"{msg.FOLDERS_FETCH_FAILED}: {res2.text}"}, status_code=sc.HTTP_BAD_REQUEST)

    folders_data = res2.json()
    flat_files_result = []

    for folder in folders_data.get("data", []):
        folder_name = folder.get("attributes", {}).get("name", "Unnamed Folder")
        files_in_folder = collect_all_files_flat(folder, headers, parent_folder_name=folder_name)
        flat_files_result.extend(files_in_folder)

    return JSONResponse(flat_files_result, status_code=sc.HTTP_OK)



