from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.calendar_utils import check_availability, book_appointment

app = FastAPI()

# Request schema for both endpoints
class AppointmentRequest(BaseModel):
    summary: str
    start_time: str  # ISO format
    end_time: str
    description: str = ""

class AvailabilityRequest(BaseModel):
    start_time: str  # ISO format
    end_time: str

# GET route to check if a time slot is free
@app.post("/check")
def check_slot(request: AvailabilityRequest):
    try:
        available = check_availability(request.start_time, request.end_time)
        return {"available": available}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# POST route to book a meeting
@app.post("/book")
def book_slot(request: AppointmentRequest):
    try:
        if check_availability(request.start_time, request.end_time):
            event = book_appointment(
                summary=request.summary,
                start_time=request.start_time,
                end_time=request.end_time,
                description=request.description
            )
            return {"status": "Booked", "event_link": event.get("htmlLink")}
        else:
            return {"status": "Time slot unavailable"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
