"""
Calendar Router — Interview Booking via Google Calendar & Cal.com
POST /api/v1/calendar/book
GET  /api/v1/calendar/slots
GET  /api/v1/calendar/callback  (OAuth)
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, timedelta
import logging

from services.calendar_service import CalendarService

logger = logging.getLogger(__name__)
router = APIRouter()
calendar_svc = CalendarService()


# ─── Models ───────────────────────────────────────────────────────────────────
class BookingRequest(BaseModel):
    recruiter_name: str = Field(..., min_length=2)
    recruiter_email: EmailStr
    company: str
    preferred_date: str   # ISO 8601: "2024-01-15"
    preferred_time: str   # "14:00"
    timezone: str = "Asia/Kolkata"
    duration_minutes: int = 30
    meeting_type: str = "video"  # "video" | "phone"
    notes: Optional[str] = None


class BookingResponse(BaseModel):
    success: bool
    booking_id: str
    calendar_link: str
    meet_link: Optional[str]
    confirmation_message: str
    event_start: str
    event_end: str


class TimeSlot(BaseModel):
    date: str
    time: str
    available: bool
    timezone: str


# ─── Routes ───────────────────────────────────────────────────────────────────
@router.get("/slots")
async def get_available_slots(
    date_from: str = Query(default=None, description="YYYY-MM-DD"),
    date_to: str = Query(default=None, description="YYYY-MM-DD"),
    timezone: str = Query(default="Asia/Kolkata"),
) -> List[TimeSlot]:
    """
    Fetch Rajnish's available interview slots from Google Calendar.
    Returns free/busy slots for the next 7 days by default.
    """
    try:
        if not date_from:
            date_from = datetime.now().strftime("%Y-%m-%d")
        if not date_to:
            date_to = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        slots = await calendar_svc.get_free_slots(date_from, date_to, timezone)
        return slots
    except Exception as e:
        logger.error(f"Slot fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/book", response_model=BookingResponse)
async def book_interview(req: BookingRequest):
    """
    Book an interview slot on Rajnish's calendar.
    Sends confirmation emails to both parties automatically.
    """
    try:
        result = await calendar_svc.create_booking(
            recruiter_name=req.recruiter_name,
            recruiter_email=req.recruiter_email,
            company=req.company,
            date_str=req.preferred_date,
            time_str=req.preferred_time,
            timezone=req.timezone,
            duration=req.duration_minutes,
            meeting_type=req.meeting_type,
            notes=req.notes,
        )

        return BookingResponse(
            success=True,
            booking_id=result["booking_id"],
            calendar_link=result["calendar_link"],
            meet_link=result.get("meet_link"),
            confirmation_message=(
                f"✅ Interview booked with Rajnish Kumar for "
                f"{req.preferred_date} at {req.preferred_time} ({req.timezone}). "
                f"A Google Meet link has been sent to {req.recruiter_email}."
            ),
            event_start=result["start"],
            event_end=result["end"],
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Booking error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Booking failed. Please try again.")


@router.get("/callback")
async def oauth_callback(code: str = Query(...)):
    """Handle Google OAuth callback for calendar access."""
    try:
        token = await calendar_svc.exchange_code(code)
        return {"message": "Calendar authorized successfully", "status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status/{booking_id}")
async def get_booking_status(booking_id: str):
    """Check booking status."""
    status = await calendar_svc.get_booking(booking_id)
    if not status:
        raise HTTPException(status_code=404, detail="Booking not found")
    return status
