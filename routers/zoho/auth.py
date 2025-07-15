from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from config import Config
import requests
from jose import jwt
from constants import response_messages as msg
from constants import status_codes as sc
from utils.shared import save_user_tokens, delete_user_tokens, get_user_tokens


templates = Jinja2Templates(directory="templates")
router = APIRouter(tags=["Zoho Auth"])

# In-memory session store (for PoC only!)
user_sessions = {}

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = user_sessions.get("current_user")
    if user:
        return HTMLResponse(
            f"""
            ✅ Logged in!<br><br>
            Name: {user['name']}<br>
            Email: {user['email']}<br>
            Zoho User ID: {user['sub']}<br><br>
            <a href="/folders/my">List My Folders & Files</a><br>
            <a href="/folders/team">List Team Folders & Files</a><br>
            <a href="/get-access-token">Get Access Token</a><br>
            <a href="/api/user-access-token?user_id=794143056.1312325977">Get API USER Access Token</a><br>
            <a href="/get-user-id">Get User ID</a><br>

            <a href="/logout">Logout</a>
            """, status_code=sc.HTTP_OK
        )
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/login")
async def login():
    zoho_auth_url = (
        f"{Config.ZOHO_ACCOUNTS_URL}/oauth/v2/auth?"
        f"scope=WorkDrive.files.ALL,WorkDrive.teamfolders.READ,openid,email,profile"
        f"&client_id={Config.CLIENT_ID}"
        f"&response_type=code"
        f"&access_type=offline"
        f"&redirect_uri={Config.REDIRECT_URI}"
        f"&prompt=consent"
    )
    return RedirectResponse(zoho_auth_url)

@router.get("/callback")
async def callback(code: str = None):
    if not code:
        return HTMLResponse(msg.NO_CODE, status_code=sc.HTTP_BAD_REQUEST)

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

    if res.status_code != sc.HTTP_OK:
        return HTMLResponse(f"{msg.TOKEN_EXCHANGE_FAILED}: {res.text}", status_code=sc.HTTP_BAD_REQUEST)

    tokens = res.json()
    id_token = tokens.get('id_token')
    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')

    if not access_token:
        return HTMLResponse(msg.NO_ACCESS_TOKEN, status_code=sc.HTTP_BAD_REQUEST)

    user_info = {'access_token': access_token}

    if id_token:
        decoded = jwt.get_unverified_claims(id_token)
        user_info['email'] = decoded.get('email', 'No email')
        user_info['sub'] = decoded.get('sub', 'No sub')
        user_info['name'] = decoded.get('name', 'No Name')
    else:
        user_info['email'] = 'No email'
        user_info['sub'] = 'No sub'
        user_info['name'] = 'No Name'

    user_sessions["current_user"] = user_info
    
    save_user_tokens(
        user_id=user_info["sub"],
        email=user_info["email"],
        name=user_info["name"],
        access_token=access_token,
        refresh_token=refresh_token
    )

    return RedirectResponse("/")

@router.get("/get-access-token")
async def get_access_token():
    user = user_sessions.get("current_user")
    if not user:
        return HTMLResponse("Not logged in.", status_code=401)
    return {"access_token": user.get("access_token")}


# @router.get("/logout")
# async def logout():
#     user_sessions.pop("current_user", None)
#     return RedirectResponse("/")

@router.get("/logout")
async def logout():
    user = user_sessions.get("current_user")
    if user:
        user_id = user.get("sub")
        delete_user_tokens(user_id)
    user_sessions.pop("current_user", None)
    return RedirectResponse("/")

@router.get("/api/user-access-token")
async def api_user_access_token(user_id: str):
    # Fetch from DB
    user_record = get_user_tokens(user_id)
    if not user_record:
        return JSONResponse({"error": "User not found or not authorized"}, status_code=401)

    refresh_token = user_record.get("refresh_token")
    if not refresh_token:
        return JSONResponse({"error": "No refresh token found"}, status_code=400)

    # Prepare refresh request
    token_url = f"{Config.ZOHO_ACCOUNTS_URL}/oauth/v2/token"
    data = {
        'refresh_token': refresh_token,
        'client_id': Config.CLIENT_ID,
        'client_secret': Config.CLIENT_SECRET,
        'grant_type': 'refresh_token'
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    res = requests.post(token_url, data=data, headers=headers)

    if res.status_code != sc.HTTP_OK:
        return JSONResponse({"error": f"Failed to refresh: {res.text}"}, status_code=400)

    tokens = res.json()
    new_access_token = tokens.get("access_token")

    if not new_access_token:
        return JSONResponse({"error": "No new access token received"}, status_code=400)

    # Update DB with new access token
    save_user_tokens(
        user_id=user_id,
        email=user_record.get("email", ""),
        name=user_record.get("name", ""),
        access_token=new_access_token,
        refresh_token=refresh_token  # We keep the same refresh token
    )

    return {"access_token": new_access_token}


@router.get("/get-user-id")
async def get_user_id():
    user = user_sessions.get("current_user")
    if not user:
        return JSONResponse({"error": "Not logged in"}, status_code=401)
    
    return {
        "user_id": user.get("sub"),
        "email": user.get("email"),
        "name": user.get("name")
    }

