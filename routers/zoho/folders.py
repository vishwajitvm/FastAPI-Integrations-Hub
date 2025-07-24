import json
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
import requests
from config import Config
from routers.zoho.auth import user_sessions
from constants import response_messages as msg
from constants import status_codes as sc
from typing import Optional
from utils.shared import get_user_tokens
from fastapi import Query
from utils.zoho_folder_helpers import get_folder_contents_json, collect_all_files_flat


router = APIRouter(prefix="/folders", tags=["Zoho Folders"])
def build_folder_hierarchy(folder, headers, depth=0, max_depth=3):
    if depth > max_depth:
        return {"name": "Max depth reached", "files": [], "subfolders": []}

    attributes = folder.get("attributes", {})
    folder_name = attributes.get("name", "Unnamed Folder")
    folder_id = folder.get("id")
    folder_url = attributes.get("permalink", "")

    folder_data = {
        "name": folder_name,
        "id": folder_id,
        "url": folder_url,
        "files": [],
        "subfolders": []
    }

    # Fetch files
    files_link = folder.get("relationships", {}).get("files", {}).get("links", {}).get("related")
    if files_link:
        files_res = requests.get(files_link, headers=headers)
        if files_res.status_code == 200:
            for file in files_res.json().get("data", []):
                file_attrs = file.get("attributes", {})
                if file.get("type") == "files" and file_attrs.get("name", "").endswith(".pdf"):
                    folder_data["files"].append({
                        "name": file_attrs.get("name", "Unnamed File"),
                        "download_url": file_attrs.get("download_url", ""),
                        "url": file_attrs.get("permalink", ""),
                        "type": file.get("type")
                    })

    # Fetch subfolders recursively
    subfolders_link = folder.get("relationships", {}).get("folders", {}).get("links", {}).get("related")
    if subfolders_link:
        subfolders_res = requests.get(subfolders_link, headers=headers)
        if subfolders_res.status_code == 200:
            for subfolder in subfolders_res.json().get("data", []):
                subfolder_data = build_folder_hierarchy(subfolder, headers, depth + 1, max_depth)
                folder_data["subfolders"].append(subfolder_data)

    return folder_data


def get_folder_contents_json(folder, headers, depth=0, max_depth=3):
    if depth > max_depth:
        return {"message": "Max recursion depth reached"}

    attributes = folder.get("attributes", {})
    folder_name = attributes.get("name", "Unnamed Folder")
    folder_id = folder.get("id", "No ID")
    folder_url = attributes.get("permalink", "")

    folder_data = {
        "name": folder_name,
        "id": folder_id,
        "url": folder_url,
        "files": [],
        "subfolders": []
    }

    # Fetch files
    files_link = folder.get("relationships", {}).get("files", {}).get("links", {}).get("related")
    if files_link:
        files_res = requests.get(files_link, headers=headers)
        if files_res.status_code == sc.HTTP_OK:
            for file in files_res.json().get("data", []):
                file_attrs = file.get("attributes", {})
                if file.get("type") == "files":  # Double-check if it's "files" or "file"
                    folder_data["files"].append({
                        "name": file_attrs.get("name", "Unnamed File"),
                        "type": file.get("type", "unknown"),
                        "url": file_attrs.get("permalink", ""),
                        "download_url": file_attrs.get("download_url", "")
                    })
        else:
            folder_data["files"].append({"error": f"Failed to fetch files: {files_res.text}"})
    else:
        folder_data["files"].append({"message": "Files listing not available for this folder."})

    # Fetch subfolders
    subfolders_link = folder.get("relationships", {}).get("folders", {}).get("links", {}).get("related")
    if subfolders_link:
        subfolders_res = requests.get(subfolders_link, headers=headers)
        if subfolders_res.status_code == sc.HTTP_OK:
            for subfolder in subfolders_res.json().get("data", []):
                subfolder_data = get_folder_contents_json(subfolder, headers, depth + 1, max_depth)
                folder_data["subfolders"].append(subfolder_data)
        else:
            folder_data["subfolders"].append({"error": f"Failed to fetch subfolders: {subfolders_res.text}"})
    else:
        folder_data["subfolders"].append({"message": "Subfolders listing not available for this folder."})

    return folder_data


@router.get("/zoho-my-folder-and-files", response_class=JSONResponse)
async def my_folders():
    user = user_sessions.get("current_user")
    if not user:
        return JSONResponse({"error": msg.NOT_LOGGED_IN}, status_code=sc.HTTP_UNAUTHORIZED)

    headers = {"Authorization": f"Zoho-oauthtoken {user['access_token']}"}
    user_url = f"{Config.ZOHO_API_URL}/workdrive/api/v1/users/me"

    res = requests.get(user_url, headers=headers)
    if res.status_code != sc.HTTP_OK:
        return JSONResponse({"error": f"{msg.FETCH_USER_FAILED}: {res.text}"}, status_code=sc.HTTP_BAD_REQUEST)

    user_id = res.json().get("data", {}).get("id")
    if not user_id:
        return JSONResponse({"error": "Failed to retrieve user ID"}, status_code=sc.HTTP_BAD_REQUEST)

    incoming_link = res.json().get("data", {}).get("relationships", {}).get("incomingfolders", {}).get("links", {}).get("related")
    if not incoming_link:
        return JSONResponse({"error": msg.NO_ROOT_FOLDER}, status_code=sc.HTTP_BAD_REQUEST)

    folders_res = requests.get(incoming_link, headers=headers)
    if folders_res.status_code != sc.HTTP_OK:
        return JSONResponse({"error": f"{msg.FOLDERS_FETCH_FAILED}: {folders_res.text}"}, status_code=sc.HTTP_BAD_REQUEST)

    structured_tree = []

    for folder in folders_res.json().get("data", []):
        print("✅ Folder fetched:", folder.get("attributes", {}).get("name"))
        tree = build_folder_hierarchy(folder, headers)
        print("✅ Tree built:", tree["name"])
        structured_tree.append(tree)

    return JSONResponse(structured_tree, status_code=sc.HTTP_OK)


@router.get("/my-teams-folder-and-files", response_class=HTMLResponse)
async def team_folders():
    user = user_sessions.get("current_user")
    if not user:
        return HTMLResponse(msg.NOT_LOGGED_IN, status_code=sc.HTTP_UNAUTHORIZED)

    headers = {"Authorization": f"Zoho-oauthtoken {user['access_token']}"}
    teams_url = f"{Config.ZOHO_API_URL}/workdrive/api/v1/users/me/teams"

    res = requests.get(teams_url, headers=headers)
    if res.status_code != sc.HTTP_OK:
        return HTMLResponse(f"{msg.FOLDERS_FETCH_FAILED}: {res.text}", status_code=sc.HTTP_BAD_REQUEST)

    output = "<h3>Team Folders & Files:</h3>"
    for team in res.json().get("data", []):
        team_id = team.get("id")
        team_name = team.get("attributes", {}).get("name", "Unnamed Team")
        if not team_id:
            continue

        output += f"<h4>Team: {team_name}</h4><ul>"
        folders_url = f"{Config.ZOHO_API_URL}/workdrive/api/v1/teamfolders?org_id={team_id}"
        folders_res = requests.get(folders_url, headers=headers)

        if folders_res.status_code != sc.HTTP_OK:
            output += f"<li>{msg.FOLDERS_FETCH_FAILED} for {team_name}: {folders_res.text}</li>"
            continue

        for folder in folders_res.json().get("data", []):
            folder_name = folder.get("attributes", {}).get("name", "Unnamed Folder")
            folder_id = folder.get("id", "No ID")
            output += f"<li>{folder_name} (ID: {folder_id})</li>"

        output += "</ul>"

    output += "<a href='/'>Back</a>"
    return HTMLResponse(output, status_code=sc.HTTP_OK)

@router.get("/my-folder-and-files-n8n", response_class=JSONResponse)
async def my_folders_n8n(user_id: str = Query(...)):

    print("im in myfolder n8n")
    tokens = get_user_tokens(user_id)
    if not tokens or not tokens.get("access_token"):
        return JSONResponse({"error": "User not logged in or token missing"}, status_code=sc.HTTP_UNAUTHORIZED)

    access_token = tokens["access_token"]
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}

    flat_files_result = []

    # 1. Fetch incoming folders
    user_url = f"{Config.ZOHO_API_URL}/workdrive/api/v1/users/me"
    res = requests.get(user_url, headers=headers)
    if res.status_code == sc.HTTP_OK:
        incoming_link = (
            res.json()
            .get("data", {})
            .get("relationships", {})
            .get("incomingfolders", {})
            .get("links", {})
            .get("related")
        )

        if incoming_link:
            res2 = requests.get(incoming_link, headers=headers)
            if res2.status_code == sc.HTTP_OK:
                for folder in res2.json().get("data", []):
                    folder_name = folder.get("attributes", {}).get("name", "Unnamed Folder")
                    files = collect_all_files_flat(folder, headers, parent_folder_name=folder_name)
                    for f in files:
                        f["source"] = "incoming"
                    flat_files_result.extend(files)

    # 2. Fetch myfolders
    myfolders_url = f"{Config.ZOHO_API_URL}/workdrive/api/v1/myfolders"
    res3 = requests.get(myfolders_url, headers=headers)
    if res3.status_code == sc.HTTP_OK:
        for folder in res3.json().get("data", []):
            folder_name = folder.get("attributes", {}).get("name", "Unnamed Folder")
            files = collect_all_files_flat(folder, headers, parent_folder_name=folder_name)
            for f in files:
                f["source"] = "myfolder"
            flat_files_result.extend(files)

 
        
    return JSONResponse(flat_files_result, status_code=sc.HTTP_OK)



