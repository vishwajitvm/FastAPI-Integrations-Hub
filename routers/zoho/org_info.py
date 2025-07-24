from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import requests
from config import Config
from routers.zoho.auth import user_sessions
from constants import response_messages as msg
from constants import status_codes as sc
from utils.shared import get_user_tokens


router = APIRouter(prefix="/api/zoho/org", tags=["Zoho Organization"])


@router.get("/basic")
async def get_basic_org_info():
    """
    Fetches basic org_id and org_name using WorkDrive 'users/me' API.
    """
    user = user_sessions.get("current_user")
    if not user:
        return JSONResponse({"error": msg.NOT_LOGGED_IN}, status_code=sc.HTTP_UNAUTHORIZED)

    headers = {"Authorization": f"Zoho-oauthtoken {user['access_token']}"}
    url = f"{Config.ZOHO_API_URL}/workdrive/api/v1/users/me"
    res = requests.get(url, headers=headers)

    if res.status_code != sc.HTTP_OK:
        return JSONResponse({"error": f"{msg.FETCH_USER_FAILED}: {res.text}"}, status_code=sc.HTTP_BAD_REQUEST)

    data = res.json().get("data", {}).get("attributes", {})

    return JSONResponse({
        "user_id": user["sub"],
        "email": user["email"],
        "name": user["name"],
        "org_id": data.get("org_id", "N/A"),
        "org_name": data.get("organization_name", "N/A")
    }, status_code=sc.HTTP_OK)


# @router.get("/details")
# async def get_detailed_org_info():
#     """
#     Fetches extended user + org details using Zoho Directory API.
#     """
#     user = user_sessions.get("current_user")
#     if not user:
#         return JSONResponse({"error": msg.NOT_LOGGED_IN}, status_code=sc.HTTP_UNAUTHORIZED)

#     headers = {"Authorization": f"Zoho-oauthtoken {user['access_token']}"}
#     url = f"{Config.ZOHO_ACCOUNTS_URL}/oauth/user/info"
#     res = requests.get(url, headers=headers)

#     if res.status_code != sc.HTTP_OK:
#         return JSONResponse({"error": f"Failed to fetch org details: {res.text}"}, status_code=sc.HTTP_BAD_REQUEST)

#     return JSONResponse(res.json(), status_code=sc.HTTP_OK)

@router.get("/details")
async def get_org_details():
    user = user_sessions.get("current_user")
    if not user:
        return JSONResponse({"error": "User not authenticated"}, status_code=401)

    access_token = user['access_token']
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}

    try:
        res = requests.get("https://www.zohoapis.com/directory/v1/organizations", headers=headers)
        if res.status_code == 200:
            return JSONResponse(res.json())
        else:
            return JSONResponse({"error": f"Failed to fetch org details: {res.text}"}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": f"Request error: {str(e)}"}, status_code=500)
    
@router.get("/{org_id}/users")
async def get_org_users(org_id: str, user_id: str = Query(...)):
    tokens = await get_user_tokens(user_id)
    access_token = tokens.get("access_token")

    url = f"https://directory.zoho.com/api/v1/orgs/{org_id}/users"
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        return JSONResponse(
            status_code=response.status_code,
            content={"error": f"HTTP error: {response.text}"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal error: {str(e)}"}
        )
