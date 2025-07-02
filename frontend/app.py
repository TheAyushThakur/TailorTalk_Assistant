import streamlit as st
import sys

import os

if "OPENROUTER_API_KEY" in st.secrets:
    os.environ["OPENROUTER_API_KEY"] = st.secrets["OPENROUTER_API_KEY"]
    os.environ["OPENROUTER_HTTP_REFERER"] = st.secrets["OPENROUTER_HTTP_REFERER"]
    os.environ["OPENROUTER_X_TITLE"] = st.secrets["OPENROUTER_X_TITLE"]
    os.environ["BACKEND_URL"] = st.secrets["BACKEND_URL"]
st.write("✅ OPENROUTER_API_KEY loaded:", "OPENROUTER_API_KEY" in st.secrets)


########## Adding project root to sys.path so "backend" is importable ##########
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.agent import chat_with_agent
st.set_page_config(page_title="TailorTalk Assistant", page_icon="🧵")
st.title("🧵 TailorTalk Assistant")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_input = st.chat_input("What would you like to ask?")

if user_input:
    # Show user message
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chat_with_agent(user_input)
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
