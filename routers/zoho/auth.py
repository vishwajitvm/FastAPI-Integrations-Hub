from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from config import Config
import requests
from jose import jwt

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
            <a href="/logout">Logout</a>
            """
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
        return HTMLResponse("No code received from Zoho", status_code=400)

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

    if res.status_code != 200:
        return HTMLResponse(f"Failed to get token: {res.text}", status_code=400)

    tokens = res.json()
    id_token = tokens.get('id_token')
    access_token = tokens.get('access_token')

    if not access_token:
        return HTMLResponse("No access_token received", status_code=400)

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

    return RedirectResponse("/")

@router.get("/logout")
async def logout():
    user_sessions.pop("current_user", None)
    return RedirectResponse("/")
