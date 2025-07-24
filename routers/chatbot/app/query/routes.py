# query/router.py
from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse

from ..query.agents.agent_executor import create_agent_executor
from ..query.tools.registry import load_all_tools
from ..query.rag.ask_question import ask_question
from config import Config

from .utils.time_parser import parse_datetime_from_query

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser

from ..db.chat_history import save_chat_log, get_chat_history

chat_router = APIRouter(prefix="/Chat", tags=["ChatBot"])
def extract_tool_name(response: dict):
    steps = response.get("intermediate_steps", [])
    for step in steps:
        if "tool" in step:
            return step["tool"]
    return None

@chat_router.post("/ask", response_class=HTMLResponse)
async def ask_route(request: Request, query: str = Form(...), user_id: str = Query(...)):
    try:
        print("\n🔵 Incoming Request -----------------------------")
        print(f"👤 User ID: {user_id}")
        print(f"📝 Query: {query}")

        # Step 1: Detect tool usage intent
        print("\n🔍 Step 1: Detecting tool usage intent...")
        llm = ChatGoogleGenerativeAI(
            google_api_key=Config.GOOGLE_API_KEY,
            model=Config.LLM_MODEL
        )
        print(f"⚙️  Using LLM Model: {Config.LLM_MODEL}")

        intent_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an assistant that decides if a user query needs to trigger a calendar booking tool."),
            ("human", "Query: {query}\n\nIs this trying to schedule a meeting or book something? Reply with 'YES' or 'NO' only.")
        ])

        tool_check_chain = LLMChain(
            llm=llm,
            prompt=intent_prompt,
            output_parser=StrOutputParser()
        )

        tool_intent = tool_check_chain.run({"query": query}).strip().upper()
        print(f"📌 Tool usage intent detected: {tool_intent}")

        # Step 2: Optional datetime parsing
        print("\n🕵️ Step 2: Attempting to parse datetime...")
        parsed_time = parse_datetime_from_query(query)
        if parsed_time:
            print(f"🕒 Parsed datetime: {parsed_time}")
            query += f" Use start_time as '{parsed_time}' in ISO 8601 format."
        else:
            print("❗ No datetime parsed from query.")

        # Step 3: If YES → Run Agent
        if tool_intent == "YES":
            print("\n🧠 Step 3: Tool intent is YES → Loading tools and invoking agent...")
            tools = load_all_tools(user_id)
            print(f"🧰 Loaded {len(tools)} tool(s): {[tool.name for tool in tools]}")

            executor = create_agent_executor(tools)
            print("🚀 Invoking agent with query...",query)

            # Before invoking the agent
            chat_history = get_chat_history(user_id)

            # print("this is our executor",executor)
            result = executor.invoke({
                "input": query,
                "context": "",  # Placeholder for now
                "chat_history": chat_history
            })
           
            print("📥 Agent returned result.")
            # After invoking agent:
            tool_executed = False
            if isinstance(result, dict):
                output = result.get("output", "")

                # ✅ Always store what the agent replied, even if it's a clarifying question
                save_chat_log(
                    user_id=user_id,
                    user_input=query,
                    bot_response=output,  # Directly from agent result
                    response_type="agent",
                    tool_used=extract_tool_name(result) if '"tool":' in output else None
                )
                if isinstance(output, str) and '"tool":' in output:
                    try:
                        output_clean = output.replace("```json", "").replace("```", "").strip()
                        import json
                        tool_call = json.loads(output_clean)

                        tool_name = tool_call.get("tool")
                        tool_input = tool_call.get("tool_input", {})

                        for tool in tools:
                            if tool.name == tool_name:
                                response = tool.invoke(tool_input)
                                tool_executed = True
                                print(f"✅ Tool '{tool_name}' executed. Response:", response)
                                # ✅ Save tool response as chat log
                                save_chat_log(
                                    user_id=user_id,
                                    user_input=query,
                                    bot_response=str(response),
                                    response_type="tool",
                                    tool_used=tool_name
                                )
                                return HTMLResponse(f"<pre>✅ Tool Call Result:\n{response}</pre>")
                        else:
                            print(f"❌ Tool '{tool_name}' not found in registry.")

                    except Exception as e:
                        print("❌ Error parsing or executing tool call:", e)
            if isinstance(result, str):
                print("🧪 Result is string:")
                print(result)
            elif isinstance(result, dict):
                print("📦 Result is dict:")
                for k, v in result.items():
                    print(f"   - {k}: {v}")
            else:
                print(f"⚠️ Unexpected result type: {type(result)}")

            # Optional: validate success
            if isinstance(result, str) and "{" not in result and "}" not in result:
                print("🌀 Tool failed or returned fallback. Running RAG fallback...")
                rag_output = ask_question(query, user_id)
                result = rag_output["result"]
            else:
                print("✅ Tool successfully invoked via agent.")
# # Step 3: If YES → Run Agent
#         if tool_intent == "YES":
#             print("\n🧪 Skipping agent and calling tool directly...")

#             tool = load_all_tools(user_id)[0]  # Assuming only one for now

#             response = tool.invoke({
#                 "title": "Pollenai Sync call",
#                 "start_time": "2025-07-24T16:30:00+05:30",
#                 "duration_minutes": 30,
#                 "attendees": ["yogesh@example.com", "nina@example.com"]
#             })

#             return HTMLResponse(f"<pre>✅ Manual Tool Call Result:\n{response}</pre>")
        else:
            # Step 4: Fallback to RAG
            print("\n🟡 Step 4: Tool not required → Running RAG...")
            rag_output = ask_question(query, user_id)
            output = rag_output["result"]
            save_chat_log(
                user_id=user_id,
                user_input=query,
                bot_response=output,
                response_type="rag",  # ✅ Mark as RAG
                tool_used=None
            )
        print("\n✅ Final Response Ready.")
        return HTMLResponse(f"<pre>{output}</pre>")

    except Exception as e:
        print(f"\n❌ ERROR occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)
