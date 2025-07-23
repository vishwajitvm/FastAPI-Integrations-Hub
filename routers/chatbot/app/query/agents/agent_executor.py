from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from config import Config
from .prompts import AGENT_SYSTEM_PROMPT

def create_agent_executor(tools: list[Tool]):
    """
    Creates and returns an AgentExecutor powered by Gemini 2.0 with tool-calling capabilities.
    """

    print("🧠 Initializing ChatGoogleGenerativeAI with model:", Config.LLM_MODEL)

    llm = ChatGoogleGenerativeAI(
        model=Config.LLM_MODEL,
        google_api_key=Config.GOOGLE_API_KEY,
        temperature=0,
        tool_choice="auto",
    )

    print(f"🛠️ Number of tools passed to agent: {len(tools)}")
    for idx, tool in enumerate(tools):
        print(f"   👉 Tool {idx+1}: {tool.name}")

    print("📜 Injecting system prompt for agent...")
    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=AGENT_SYSTEM_PROMPT
    )

    print("🚀 Creating AgentExecutor...")
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        return_intermediate_steps=True  # helpful to debug
    )

    print("✅ AgentExecutor successfully created.")
    return executor
