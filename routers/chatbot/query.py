# query.py
import sys, os, json, re, urllib.parse
from datetime import datetime, timedelta
import requests
from config import Config
from fastapi import APIRouter, Request, Query, Form
from fastapi.responses import HTMLResponse, JSONResponse
from langchain_astradb import AstraDBVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from utils.shared import save_user_tokens, delete_user_tokens, get_user_tokens
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts.chat import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage, HumanMessage

# Add root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

chat_router = APIRouter(prefix="/Chat", tags=["ChatBot"])

from pydantic import BaseModel,field_validator
from langchain.tools import StructuredTool

prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content=(
    "You are a helpful assistant that can answer questions and schedule meetings. "
    "If the user wants to schedule a meeting, call the BOOK_MEETING tool. "
    "ONLY use the BOOK_MEETING tool ONCE per response. "
    "Format `start_time` in **full ISO 8601** format with timezone offset. "
    "Example: '2025-07-18T15:30:00+05:30' (India Standard Time is +05:30). "
    "Do NOT use formats like 'July 18, 3:30 PM' or '2025-07-18 15:30'. "
    "Do NOT omit the timezone — it must be included."
    )),
    HumanMessage(content="{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),  # ✅ Required
])
from typing import List

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
def make_structured_booking_tool(user_id: str):
    def book(title: str, start_time: str, duration_minutes: int, attendees: list[str]):
        data = MeetingInput(
            title=title,
            start_time=start_time,
            duration_minutes=duration_minutes,
            attendees=attendees
        )
        return _wrapped_booking(json.dumps(data.dict()), user_id)

    return StructuredTool.from_function(
        func=book,
        name="BOOK_MEETING",
        description=(
        "Schedules a meeting using Zoho Calendar. "
        "Inputs must be: "
        "- `title`: string, e.g., 'Marketing Plan Review'. "
        "- `start_time`: ISO 8601 string with timezone, e.g., '2025-07-18T15:30:00+05:30'. "
        "- `duration_minutes`: integer, e.g., 60. "
        "- `attendees`: list of emails, e.g., ['alice@example.com', 'bob@example.com']."
        ),
        args_schema=MeetingInput
    )


# AstraDB Vectorstore
def get_vectorstore(user_id: str):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return AstraDBVectorStore(
        embedding=embeddings,
        collection_name=Config.ASTRA_COLLECTION,
        api_endpoint=Config.ASTRA_DB_ENDPOINT,
        token=Config.ASTRA_DB_API_KEY,
    )

# QA using Gemini Flash
def ask_question(query: str, user_id: str):
    vectorstore = get_vectorstore(user_id)
    is_summary = any(word in query.lower() for word in ["summarize", "summary", "explain", "overview"])
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 7})

    prompt_template = None
    if is_summary:
        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""
                You are an expert at making complex information easy to understand.
                Summarize the following content in a clear, simple, and engaging way,
                as if explaining to a beginner.

                Context:
                {context}

                User request:
                {question}

                Answer:
            """
        )

    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatGoogleGenerativeAI(google_api_key=Config.GOOGLE_API_KEY, model="models/gemini-2.0-flash"),
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt_template} if prompt_template else {}
    )
    result = qa_chain.invoke(query)
    return result["result"]

# Get Calendar ID
def get_calendar_id(access_token: str):
    print("📡 Calling Zoho Calendar API to fetch calendar ID")
    url = "https://calendar.zoho.com/api/v1/calendars"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch calendars: {response.text}")

    calendars = response.json().get("calendars", [])
    if not calendars:
        raise Exception("No calendars found")

    return calendars[0]["uid"]

# Refresh access token
def get_access_token_for_user(user_id: str):
    user_record = get_user_tokens(user_id)
    if not user_record:
        raise Exception("❌ User not authorized")

    refresh_token = user_record.get("refresh_token")
    if not refresh_token:
        raise Exception("❌ No refresh token found")

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
        raise Exception(f"❌ Failed to refresh token: {res.text}")

    tokens = res.json()
    access_token = tokens.get("access_token")
    if not access_token:
        raise Exception("❌ No access token received")

    calendar_id = get_calendar_id(access_token)
    print(f"✅ Refreshed token & got calendar ID: {calendar_id}")

    save_user_tokens(
        user_id=user_id,
        email=user_record.get("email", ""),
        name=user_record.get("name", ""),
        access_token=access_token,
        refresh_token=refresh_token
    )

    return access_token, calendar_id

# Tool wrapper
def _wrapped_booking(prompt: str, user_id: str):
    import json, re

    try:
        print("📨 Booking Zoho Calendar meeting...")
        print("🧠 Tool input:\n", prompt)
        print("🔍 Trying to extract JSON with regex BOOK_MEETING {{...}}")
        # Try to extract JSON block from various agent formats
        json_like_match = (
            re.search(r"BOOK_MEETING.*?```(?:json)?\s*({.*?})\s*```", prompt, re.DOTALL) or
            re.search(r"BOOK_MEETING\s*{(.*?)}", prompt, re.DOTALL) or
            re.search(r"Action Input:\s*(\{.*?\})", prompt, re.DOTALL) or
            re.search(r"({.*})", prompt.strip(), re.DOTALL)  # <-- final fallback
        )


        if not json_like_match:
            print("❌ All JSON extract regexes failed.")
            return "❌ Could not find a valid BOOK_MEETING block."

        json_text = json_like_match.group(1).strip()
        print("✅ Extracted JSON:\n", json_text)

        # 🔧 FIX: clean up invalid formatting before JSON parsing
        json_text = re.sub(r'\n\s*', '', json_text)
        json_text = json_text.replace("“", '"').replace("”", '"')


        meeting_data = json.loads(json_text)


        # Check required fields
        required_keys = {"title", "start_time", "duration_minutes", "attendees"}
        if not required_keys.issubset(meeting_data):
            return f"❌ Missing some input keys: {required_keys - meeting_data.keys()}"

        title = meeting_data["title"]
        start_time = meeting_data["start_time"]
        duration_minutes = meeting_data["duration_minutes"]
        attendees = meeting_data["attendees"]

        access_token, calendar_id = get_access_token_for_user(user_id)
        return book_zoho_meeting(
            calendar_id=calendar_id,
            access_token=access_token,
            title=title,
            start_time=start_time,
            duration_minutes=duration_minutes,
            attendees=attendees,
        )

    except json.JSONDecodeError as e:
        return f"❌ Failed to parse JSON block: {e}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

# Book meeting via Zoho API
from datetime import timezone

def book_zoho_meeting(calendar_id, access_token, title, start_time, duration_minutes, attendees):
    print("📨 Booking Zoho Calendar meeting...")

    # Parse and convert to UTC
    start = datetime.fromisoformat(start_time).astimezone(timezone.utc)
    end = start + timedelta(minutes=duration_minutes)

    formatted_start = start.strftime('%Y%m%dT%H%M%SZ')
    formatted_end = end.strftime('%Y%m%dT%H%M%SZ')

    event_data = {
        "title": title,
        "dateandtime": {
            "timezone": "Asia/Kolkata",  # still local timezone for display
            "start": formatted_start,
            "end": formatted_end
        },
        "attendees": [{"email": email, "status": "NEEDS-ACTION"} for email in attendees],
        "richtext_description": "<div><p>Scheduled via FastAPI Bot</p></div>",
        "reminders": [{"action": "popup", "minutes": -15}]
        # Omit "conference": "zmeeting" if user has no meeting org
    }

    encoded_eventdata = urllib.parse.quote(json.dumps(event_data))
    url = f"https://calendar.zoho.com/api/v1/calendars/{calendar_id}/events?eventdata={encoded_eventdata}"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        print("✅ Meeting booked successfully.")
        return response.json()
    else:
        print(f"❌ Booking failed: {response.status_code} | {response.text}")
        return {"error": response.text}

# Main chat endpoint
@chat_router.post("/ask", response_class=HTMLResponse)
async def ask_route(request: Request, query: str = Form(...), user_id: str = Query(...)):
    try:
        print(f"🔍 User {user_id} asked: {query}")

        # 🧪 Manual test input (optional)
        test_booking_data = {
            "title": "Demo Call for testing",
            "start_time": "2025-07-18T12:00:00+05:30",
            "duration_minutes": 30,
            "attendees": ["mithilesh@example.com", "manager@example.com"]
        }

        # 👉 ONLY run this if you want to test without the LLM
        booking_tool = make_structured_booking_tool(user_id).func
        result = booking_tool(**test_booking_data)
        return HTMLResponse(f"<pre>{result}</pre>")

        tools = [make_structured_booking_tool(user_id)]

        llm = ChatGoogleGenerativeAI(
            google_api_key=Config.GOOGLE_API_KEY,
            model="models/gemini-2.0-flash"
        )

        agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
        executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        result = executor.invoke({"input": query, "chat_history": []})

        return HTMLResponse(f"""
            <html><body>
            <h3>🤖 Result</h3>
            <p>{result}</p>
            <a href="/">🔙 Back</a>
            </body></html>
        """)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

