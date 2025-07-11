import json
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import requests
from config import Config
from routers.zoho.auth import user_sessions
import html
from constants import response_messages as msg
from constants import status_codes as sc

router = APIRouter(prefix="/folders", tags=["Zoho Folders"])

# @router.get("/my", response_class=HTMLResponse)
# async def my_folders():
#     user = user_sessions.get("current_user")
#     if not user:
#         return HTMLResponse(msg.NOT_LOGGED_IN, status_code=sc.HTTP_UNAUTHORIZED)

#     access_token = user['access_token']
#     headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}

#     user_url = f"{Config.ZOHO_API_URL}/workdrive/api/v1/users/me"
#     res = requests.get(user_url, headers=headers)

#     if res.status_code != sc.HTTP_OK:
#         return HTMLResponse(f"{msg.FETCH_USER_FAILED}: {res.text}", status_code=sc.HTTP_BAD_REQUEST)

#     user_data = res.json()
#     root_folder_id = (
#         user_data.get("data", {})
#         .get("attributes", {})
#         .get("root_folder_id")
#     )

#     if not root_folder_id:
#         return HTMLResponse(msg.NO_ROOT_FOLDER, status_code=sc.HTTP_BAD_REQUEST)

#     files_url = f"{Config.ZOHO_API_URL}/workdrive/api/v1/folders/{root_folder_id}/files"
#     res2 = requests.get(files_url, headers=headers)

#     if res2.status_code == sc.HTTP_OK:
#         files = res2.json()
#         output = "<h3>My Folders & Files:</h3><ul>"
#         for file in files.get("data", []):
#             fname = file.get("attributes", {}).get("name", "Unnamed")
#             ftype = file.get("type", "unknown")
#             output += f"<li>{fname} — {ftype}</li>"
#         output += "</ul><a href='/'>Back</a>"
#         return HTMLResponse(output, status_code=sc.HTTP_OK)
#     else:
#         return HTMLResponse(f"{msg.FOLDERS_FETCH_FAILED}: {res2.text}", status_code=sc.HTTP_BAD_REQUEST)

def get_folder_contents(folder, headers, level=0):
    output = ""
    indent = "&nbsp;" * (level * 4)

    folder_name = html.escape(folder.get("attributes", {}).get("name", "Unnamed Folder"))
    folder_id = folder.get("id", "No ID")
    output += f"{indent}<li><strong>{folder_name} (ID: {folder_id})</strong><ul>"

    # Check files link
    files_link = (
        folder
        .get("relationships", {})
        .get("files", {})
        .get("links", {})
        .get("related")
    )

    if files_link:
        files_res = requests.get(files_link, headers=headers)
        if files_res.status_code == sc.HTTP_OK:
            files_data = files_res.json()
            files_list = files_data.get("data", [])
            if not files_list:
                output += f"{indent}<li>No files</li>"
            else:
                for file in files_list:
                    file_name = html.escape(file.get("attributes", {}).get("name", "Unnamed File"))
                    file_type = html.escape(file.get("type", "unknown"))
                    output += f"{indent}<li>{file_name} — {file_type}</li>"
        else:
            output += f"{indent}<li>Failed to fetch files: {files_res.text}</li>"
    else:
        output += f"{indent}<li>Files listing not available for this folder.</li>"

    # Check subfolders link
    subfolders_link = (
        folder
        .get("relationships", {})
        .get("folders", {})
        .get("links", {})
        .get("related")
    )

    if subfolders_link:
        subfolders_res = requests.get(subfolders_link, headers=headers)
        if subfolders_res.status_code == sc.HTTP_OK:
            subfolders_data = subfolders_res.json()
            subfolders_list = subfolders_data.get("data", [])
            for subfolder in subfolders_list:
                # Recursively call for each subfolder
                output += get_folder_contents(subfolder, headers, level + 1)
        else:
            output += f"{indent}<li>Failed to fetch subfolders: {subfolders_res.text}</li>"
    else:
        output += f"{indent}<li>Subfolders listing not available for this folder.</li>"

    output += f"{indent}</ul></li>"
    return output


@router.get("/my", response_class=HTMLResponse)
async def my_folders():
    user = user_sessions.get("current_user")
    if not user:
        return HTMLResponse(msg.NOT_LOGGED_IN, status_code=sc.HTTP_UNAUTHORIZED)

    access_token = user['access_token']
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}

    # Fetch user details
    user_url = f"{Config.ZOHO_API_URL}/workdrive/api/v1/users/me"
    res = requests.get(user_url, headers=headers)

    if res.status_code != sc.HTTP_OK:
        return HTMLResponse(f"{msg.FETCH_USER_FAILED}: {res.text}", status_code=sc.HTTP_BAD_REQUEST)

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
        return HTMLResponse(msg.NO_ROOT_FOLDER, status_code=sc.HTTP_BAD_REQUEST)

    # Fetch incoming folders
    res2 = requests.get(incoming_folders_link, headers=headers)
    if res2.status_code != sc.HTTP_OK:
        return HTMLResponse(f"{msg.FOLDERS_FETCH_FAILED}: {res2.text}", status_code=sc.HTTP_BAD_REQUEST)

    folders_data = res2.json()
    output = "<h3>Incoming Folders & All Nested Files/Folders:</h3><ul>"

    for folder in folders_data.get("data", []):
        output += get_folder_contents(folder, headers, level=1)

    output += "</ul><a href='/'>Back</a>"
    return HTMLResponse(output, status_code=sc.HTTP_OK)


@router.get("/team", response_class=HTMLResponse)
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
