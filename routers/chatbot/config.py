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
    ASTRA_DB_API_KEY = os.getenv("ASTRA_DB_API_KEY")
    ASTRA_DB_ENDPOINT = "https://3a001a12-2fc2-4aa1-ba00-4b8fff800e7d-us-east-2.apps.astra.datastax.com"
    ASTRA_COLLECTION = "sop_rag"
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    LLM_MODEL = "models/gemini-2.0-flash"
