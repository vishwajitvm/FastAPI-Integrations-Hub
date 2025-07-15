import requests
from constants import status_codes as sc

def get_folder_contents_json(folder, headers):
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
            for file in files_list:
                file_attributes = file.get("attributes", {})
                file_name = file_attributes.get("name", "Unnamed File")
                file_type = file.get("type", "unknown")
                file_url = file_attributes.get("permalink", "")

                folder_data["files"].append({
                    "name": file_name,
                    "type": file_type,
                    "url": file_url
                })
        else:
            folder_data["files"].append({
                "error": f"Failed to fetch files: {files_res.text}"
            })
    else:
        folder_data["files"].append({
            "message": "Files listing not available for this folder."
        })

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
                subfolder_data = get_folder_contents_json(subfolder, headers)
                folder_data["subfolders"].append(subfolder_data)
        else:
            folder_data["subfolders"].append({
                "error": f"Failed to fetch subfolders: {subfolders_res.text}"
            })
    else:
        folder_data["subfolders"].append({
            "message": "Subfolders listing not available for this folder."
        })

    return folder_data

def collect_all_files_flat(folder, headers, parent_folder_name="", parent_subfolder_name=""):
    files_flat = []

    current_folder_name = folder.get("attributes", {}).get("name", "Unnamed Folder")

    # Files directly in this folder
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
            for file in files_list:
                file_attributes = file.get("attributes", {})
                files_flat.append({
                    "name": file_attributes.get("name", "Unnamed File"),
                    "id": file.get("id", "No ID"),
                    "url": file_attributes.get("permalink", ""),
                    "folder_name": parent_folder_name or current_folder_name,
                    "subfolder_name": parent_subfolder_name
                })

    # Subfolders
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
                subfolder_name = subfolder.get("attributes", {}).get("name", "Unnamed Subfolder")
                # Recursively collect files from subfolder
                subfolder_files = collect_all_files_flat(
                    subfolder, headers,
                    parent_folder_name=current_folder_name,
                    parent_subfolder_name=subfolder_name
                )
                files_flat.extend(subfolder_files)

    return files_flat

