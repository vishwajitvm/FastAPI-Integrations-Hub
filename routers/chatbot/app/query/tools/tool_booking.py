from typing import List
from pydantic import BaseModel, field_validator, model_validator
from langchain.tools import StructuredTool
from ..utils.time_parser import parse_datetime_from_query
import json
from .zoho_booking_api import wrapped_booking_tool  # 👈 wraps booking call + regex extract

# 🎯 Tool input schema
class MeetingInput(BaseModel):
    title: str
    start_time: str  # ISO 8601 with timezone offset
    duration_minutes: int
    attendees: List[str]

    @field_validator("attendees", mode="before")
    @classmethod
    def parse_attendees(cls, v):
        if isinstance(v, str):
            import ast
            try:
                return ast.literal_eval(v)
            except Exception:
                raise ValueError("Invalid format for attendees. Must be a list of emails.")
        return v
    

# 🛠️ StructuredTool factory
def make_tool(user_id: str) -> StructuredTool:
    def book(title: str, start_time: str, duration_minutes: int, attendees: list[str]):
        print("🔥 BOOK_MEETING tool triggered with:", title, start_time, duration_minutes, attendees)

        parsed_time = parse_datetime_from_query(start_time)
    
        # 👇 If parsing fails or you're forcing manual override
        if not parsed_time:
            print("⚠️ No datetime parsed — using hardcoded fallback.")
            # Hardcode ISO datetime for now
            parsed_time = "2025-07-23T13:30:00+05:30"

        start_time = parsed_time


        data = MeetingInput(
            title=title,
            start_time=start_time,
            duration_minutes=duration_minutes,
            attendees=attendees
        )

        result = wrapped_booking_tool(json.dumps(data.model_dump()), user_id)
        print("Tool booking data:", data.model_dump())
        print("Calling wrapped_booking_tool with JSON:", json.dumps(data.model_dump()))
        # ✅ Convert to string response
        if isinstance(result, dict):
            if "error" in result:
                return f"❌ Failed to book meeting: {result['error']}"
            return (
                f"✅ Meeting '{title}' booked on {start_time} for {duration_minutes} minutes "
                f"with {', '.join(attendees)}."
            )
        

        return str(result)  # fallback for non-dict results

    return StructuredTool.from_function(
        func=book,
        name="BOOK_MEETING",
        description=(
            "Schedules a meeting using Zoho Calendar.\n"
            "Inputs must be:\n"
            "- `title`: string, e.g., 'Marketing Plan Review'\n"
            "- `start_time`: ISO 8601 string with timezone, e.g., '2025-07-18T15:30:00+05:30'\n"
            "- `duration_minutes`: integer, e.g., 60\n"
            "- `attendees`: list of emails, e.g., ['alice@example.com', 'bob@example.com']"
        ),
        args_schema=MeetingInput
    )
