from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz
import os
import json
import base64
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()

CALENDAR_ID = 'ayushthakur6005@gmail.com'  
SCOPES = ['https://www.googleapis.com/auth/calendar']

base64_creds = os.getenv("GOOGLE_CREDENTIALS_BASE64")

if not base64_creds:
    raise ValueError("GOOGLE_CREDENTIALS_BASE64 not found in environment!")

# Decode and parse the credentials
decoded_bytes = base64.b64decode(base64_creds)
service_account_info = json.loads(decoded_bytes)

# Build credentials from dict
credentials = service_account.Credentials.from_service_account_info(
    service_account_info, scopes=SCOPES
)


service = build('calendar', 'v3', credentials=credentials)


def check_availability(start_time: str, end_time: str) -> bool:
    """
    Checks if the time slot is free using FreeBusy API.
    """
    body = {
        "timeMin": start_time,
        "timeMax": end_time,
        "timeZone": "UTC",
        "items": [{"id": CALENDAR_ID}]
    }

    freebusy_result = service.freebusy().query(body=body).execute()
    busy_times = freebusy_result["calendars"][CALENDAR_ID]["busy"]

    return len(busy_times) == 0  # True if slot is free


def book_appointment(summary: str, start_time: str, end_time: str, description="") -> dict:
    event = {
        'summary': summary,
        'description': description,
        'start': {'dateTime': start_time},
        'end': {'dateTime': end_time},
    }

    print("EVENT BEING SENT:", event)

    event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return event

print("Decoding successful. Service account loaded.")


