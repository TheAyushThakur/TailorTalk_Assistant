# TailorTalk 🧵🤖

A conversational AI agent that books appointments on Google Calendar via chat.

## Features
- Natural conversation with users
- Google Calendar integration using Service Account
- Built using FastAPI, Langchain, and Streamlit

## Run Locally

uvicorn backend.main:app --reload
streamlit run frontend/app.py

## Instructions
usage instructions while talking to TailorTalk chatbot:
provide proper prompts like:
"is 3 AM available for 4 July 2025" or "Book a slot for 3 AM on 3 July 2025"
Don't write "Tomorrow" or "Today" or "Night" or "Morning"
Provide clear instructions with Date, Time, Month and year.

