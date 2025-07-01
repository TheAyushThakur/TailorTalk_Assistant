import os
import requests
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.tools import tool
from dotenv import load_dotenv
from datetime import datetime
from dateutil import parser
import pytz
import streamlit as st

openrouter_key = os.getenv("OPENROUTER_API_KEY") or st.secrets.get("OPENROUTER_API_KEY")

def ensure_utc(time_str: str) -> str:
    try:
        dt = parser.parse(time_str, fuzzy=True)

        # ✅ Always assume Asia/Kolkata if no tzinfo present
        if dt.tzinfo is None:
            ist = pytz.timezone("Asia/Kolkata")
            dt = ist.localize(dt)

        return dt.astimezone(pytz.UTC).isoformat()
    
    except Exception as e:
        raise ValueError(f"Invalid time format: {time_str}") from e

# Load LLM
llm = ChatOpenAI(
    temperature=0.2,
    model_name="meta-llama/llama-3-70b-instruct",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=openrouter_key
)
# Backend API URL
BASE_URL = "http://localhost:8000"

# Tool to check availability
@tool
def check_slot(start_time: str, end_time: str) -> str:
    """
    Use this tool to check if a time slot is free in the calendar.
    """
    payload = {
        "start_time": ensure_utc(start_time),
        "end_time": ensure_utc(end_time),
        }
    print("📤 check_slot payload:", payload)  # ✅ DEBUG LOG

    response = requests.post(f"{BASE_URL}/check", json=payload)
    result = response.json()
    print("📥 check_slot response:", result)  # ✅ DEBUG LOG

    return f"The slot is {'available ✅' if result.get('available') else 'not available ❌'}."

# Tool to book a slot
@tool
def book_slot(summary: str, start_time: str, end_time: str, description: str = "") -> str:
    """
    Use this tool to book a calendar event.
    Must provide summary, start_time, end_time. Description optional.
    """
    payload = {
        "summary": summary,
        "start_time": ensure_utc(start_time),
        "end_time": ensure_utc(end_time),
        "description": description
    }
    response = requests.post(f"{BASE_URL}/book", json=payload)
    result = response.json()
    
    if result.get("status") == "Booked":
        return f"Meeting booked successfully. Link: {result.get('event_link', 'N/A')}"
    else:
        return "Time slot is unavailable. Please try another time."

# List of tools
tools = [check_slot, book_slot]

# Create agent

today = datetime.utcnow().strftime("%Y-%m-%d")

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={
    "system_message": f"You are TailorTalk, a helpful calendar assistant. Today is {today}. "
                      f"Assume all user input is in India Standard Time (IST, UTC+05:30). "
                      f"Always return times in ISO 8601 format like 2025-07-03T10:00:00+05:30"
    },
    input_variables = ["input"],
    max_iterations = 3
)

def chat_with_agent(user_input: str):
    result = agent.invoke({"input": user_input})
    return result["output"]
