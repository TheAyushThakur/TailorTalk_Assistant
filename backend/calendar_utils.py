from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'backend/service_account.json'  
CALENDAR_ID = 'ayushthakur6005@gmail.com'  

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
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



