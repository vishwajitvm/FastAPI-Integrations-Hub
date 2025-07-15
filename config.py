import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "supersecret")
    CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
    CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("ZOHO_REDIRECT_URI")
    ZOHO_ACCOUNTS_URL = "https://accounts.zoho.com"
    ZOHO_API_URL = "https://www.zohoapis.com"
    MONGO_URI = os.getenv("MONGO_URI")
