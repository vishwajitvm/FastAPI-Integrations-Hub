import json
import re
import requests
import urllib.parse
from datetime import datetime, timedelta, timezone
from config import Config
from utils.shared import save_user_tokens, get_user_tokens

#  Refresh token and get calendar ID
def get_access_token_for_user(user_id: str):
    user_record = get_user_tokens(user_id)
    if not user_record:
        raise Exception(" User not authorized")

    refresh_token = user_record.get("refresh_token")
    if not refresh_token:
        raise Exception(" No refresh token found")

    token_url = f"{Config.ZOHO_ACCOUNTS_URL}/oauth/v2/token"
    data = {
        'refresh_token': refresh_token,
        'client_id': Config.CLIENT_ID,
        'client_secret': Config.CLIENT_SECRET,
        'grant_type': 'refresh_token'
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    res = requests.post(token_url, data=data, headers=headers)

    if res.status_code != 200:
        raise Exception(f" Failed to refresh token: {res.text}")

    tokens = res.json()
    access_token = tokens.get("access_token")
    if not access_token:
        raise Exception("No access token received")

    calendar_id = get_calendar_id(access_token)
    print(f"Refreshed token & got calendar ID: {calendar_id}")

    save_user_tokens(
        user_id=user_id,
        email=user_record.get("email", ""),
        name=user_record.get("name", ""),
        access_token=access_token,
        refresh_token=refresh_token
    )
    print(f"Got access_token for {user_record.get('email')}: {access_token[:6]}...")

    return access_token, calendar_id

#  Fetch first calendar ID
def get_calendar_id(access_token: str):
    url = "https://calendar.zoho.com/api/v1/calendars"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    response = requests.get(url, headers=headers)

    print("Calendars JSON:", response.json())  # 👈 See what's available

    calendars = response.json().get("calendars", [])
    return calendars[0]["uid"] if calendars else None


# Book meeting using Zoho API
def book_zoho_meeting(calendar_id, access_token, title, start_time, duration_minutes, attendees):
    start = datetime.fromisoformat(start_time).astimezone(timezone.utc)
    end = start + timedelta(minutes=duration_minutes)

    formatted_start = start.strftime('%Y%m%dT%H%M%SZ')
    formatted_end = end.strftime('%Y%m%dT%H%M%SZ')

    event_data = {
        "title": title,
        "dateandtime": {
            "timezone": "Asia/Kolkata",
            "start": formatted_start,
            "end": formatted_end
        },
        "attendees": [{"email": email, "status": "NEEDS-ACTION"} for email in attendees],
        "richtext_description": "<div><p>Scheduled via FastAPI Bot</p></div>",
        "reminders": [{"action": "popup", "minutes": -15}]
    }

    encoded_eventdata = urllib.parse.quote(json.dumps(event_data))
    url = f"https://calendar.zoho.com/api/v1/calendars/{calendar_id}/events?eventdata={encoded_eventdata}"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    print("Booking event data:\n", json.dumps(event_data, indent=2))
    print("Requesting URL:", url)
    print("Headers:", headers)

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        print("Meeting booked successfully.")
        return f"✅ Meeting booked for '{title}' at {start_time} with {', '.join(attendees)}"
    else:
        print(f"Booking failed: {response.status_code} | {response.text}")
        return {"error": response.text}


#  Tool function wrapper
def wrapped_booking_tool(prompt: str, user_id: str):
    try:
        print("Booking Zoho Calendar meeting...")
        print("Prompt received:", prompt)

        meeting_data = json.loads(prompt)
        print("Parsed meeting data:", meeting_data)

        access_token, calendar_id = get_access_token_for_user(user_id)
        print(f"Using calendar: {calendar_id}, access_token: {access_token[:5]}...")

        result = book_zoho_meeting(
            calendar_id=calendar_id,
            access_token=access_token,
            title=meeting_data["title"],
            start_time=meeting_data["start_time"],
            duration_minutes=meeting_data["duration_minutes"],
            attendees=meeting_data["attendees"]
        )

        print("Zoho API booking result:", result)
        return result

    except Exception as e:
        print("❌ Booking failed:", str(e))
        return f"Unexpected error: {str(e)}"
