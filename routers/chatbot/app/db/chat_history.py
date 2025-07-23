# db/chat_history.py

from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage
from utils.shared import chatlogs_collection  # 👈 from your updated mongo.py


def save_chat_log(user_id: str, user_input: str, bot_response: str, response_type="rag", tool_used=None):
    """
    Save a single chat turn to MongoDB.
    """
    chatlogs_collection.insert_one({
        "user_id": user_id,
        "user_input": user_input,
        "bot_response": bot_response,
        "type": response_type,
        "tool_used": tool_used,
        "timestamp": datetime.now()
    })


def get_chat_history(user_id: str, limit: int = 20) -> list:
    """
    Fetch recent chat history for a user, sorted by timestamp ASC.
    Returns as a list of LangChain-compatible messages.
    """
    history = []

    cursor = chatlogs_collection.find(
        {"user_id": user_id},
        sort=[("timestamp", 1)]
    ).limit(limit)

    for doc in cursor:
        history.append(HumanMessage(content=doc["user_input"]))
        history.append(AIMessage(content=doc["bot_response"]))

    return history
