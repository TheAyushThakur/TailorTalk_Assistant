import os
import requests
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain_community.chat_models import ChatOpenAI 
from langchain.tools import tool
from dotenv import load_dotenv
from datetime import datetime
from dateutil import parser
import pytz
import streamlit as st

# Load environment first
load_dotenv()

# Get API key with fallback
openrouter_key = os.getenv("OPENROUTER_API_KEY") or st.secrets.get("OPENROUTER_API_KEY")

def ensure_utc(time_str: str) -> str:
    """Convert any time string to UTC ISO format"""
    try:
        dt = parser.parse(time_str, fuzzy=True)
        if dt.tzinfo is None:
            ist = pytz.timezone("Asia/Kolkata")
            dt = ist.localize(dt)
        return dt.astimezone(pytz.UTC).isoformat()
    except Exception as e:
        raise ValueError(f"Invalid time format: {time_str}. Use formats like '3pm tomorrow' or '2025-07-04 15:00'") from e

# Initialize LLM with proper headers
llm = ChatOpenAI(
    temperature=0.2,
    model_name="meta-llama/llama-3-70b-instruct",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=openrouter_key,
    model_kwargs={
        "headers":{
        "HTTP-Referer": "https://tailortalkassistant.streamlit.app/",
        "X-Title": "TailorTalk Assistant"
    }
    }
)

# Backend API URL
BASE_URL = "https://web-production-0006.up.railway.app/"

@tool
def check_slot(start_time: str, end_time: str) -> str:
    """Check calendar availability between start_time and end_time (in IST)"""
    try:
        payload = {
            "start_time": ensure_utc(start_time),
            "end_time": ensure_utc(end_time)
        }
        response = requests.post(f"{BASE_URL}/check", json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        return f"Slot {'available' if result.get('available') else 'unavailable'}"
    except Exception as e:
        return f"Error checking slot: {str(e)}"

@tool
def book_slot(summary: str, start_time: str, end_time: str, description: str = "") -> str:
    """Book a calendar slot with title, start/end times (IST), and optional notes"""
    try:
        payload = {
            "summary": summary,
            "start_time": ensure_utc(start_time),
            "end_time": ensure_utc(end_time),
            "description": description
        }
        response = requests.post(f"{BASE_URL}/book", json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        return f"Booked: {result.get('event_link', 'No link provided')}"
    except Exception as e:
        return f"Booking failed: {str(e)}"

# Initialize agent
today = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d")

agent = initialize_agent(
    tools=[check_slot, book_slot],
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=3,
    agent_kwargs={
        "system_message": f"""You are TailorTalk Assistant. Today is {today} (IST).
        Key rules:
        1. Always assume times are in India Standard Time (UTC+5:30)
        2. Confirm availability before booking
        3. Return times in ISO format (YYYY-MM-DDTHH:MM:SS+05:30)"""
    }
)

def chat_with_agent(user_input: str) -> str:
    """Safely handle agent interactions"""
    try:
        result = agent.invoke({"input": user_input})
        return result["output"]
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"