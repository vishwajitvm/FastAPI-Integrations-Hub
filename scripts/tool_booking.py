# scripts/test_booking.py
import sys
import os

# Add the project root to sys.path so absolute imports work
sys.path.append(os.path.abspath("."))

from ..routers.chatbot.app.query.tools.zoho_booking_api import wrapped_booking_tool

prompt = '''
BOOK_MEETING {
    "title": "Weekly Project Sync",
    "start_time": "2025-07-21T12:00:00+05:30",
    "duration_minutes": 60,
    "attendees": ["alice@bee-logical.com", "bob@bee-logical.com"]
}
'''

user_id = "your-user-id"  # 🔁 Replace with actual test user_id
result = wrapped_booking_tool(prompt, user_id)
print(result)
