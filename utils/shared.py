import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "zoho_auth")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

users_collection = db["users"]
chatlogs_collection = db["chat_logs"]


def save_user_tokens(user_id, email, name, access_token, refresh_token):
    users_collection.update_one(
        {"zoho_id": user_id},
        {
            "$set": {
                "email": email,
                "name": name,
                "access_token": access_token,
                "refresh_token": refresh_token
            }
        },
        upsert=True
    )

def get_user_tokens(user_id):
    return users_collection.find_one({"zoho_id": user_id})

def delete_user_tokens(user_id):
    return users_collection.delete_one({"zoho_id": user_id})
