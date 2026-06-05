"""
Calendar Service — Google Calendar + Cal.com Integration
"""

import logging
import uuid
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pytz
from config import settings

logger = logging.getLogger(__name__)


class CalendarService:
    """
    Handles:
    - Google Calendar OAuth + event creation
    - Cal.com API integration
    - Free/busy slot detection
    - Email confirmations
    """

    def __init__(self):
        self._credentials = None

    async def get_credentials(self):
        """Get/refresh Google OAuth credentials."""
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import Flow

        if self._credentials and self._credentials.valid:
            return self._credentials

        # In production, load from Supabase/Redis
        # For now, use service account or stored token
        raise NotImplementedError("Set up OAuth credentials in .env")

    async def get_free_slots(
        self, date_from: str, date_to: str, timezone: str = "Asia/Kolkata"
    ) -> List[Dict]:
        """
        Query Google Calendar free/busy API and return available slots.
        Returns 30-min slots during business hours (9 AM - 6 PM IST).
        """
        tz = pytz.timezone(timezone)
        from_dt = datetime.strptime(date_from, "%Y-%m-%d")
        to_dt = datetime.strptime(date_to, "%Y-%m-%d")

        slots = []
        current = from_dt

        while current <= to_dt:
            # Skip weekends
            if current.weekday() < 5:
                # Generate 30-min slots from 9 AM to 6 PM
                slot_time = current.replace(hour=9, minute=0)
                end_of_day = current.replace(hour=18, minute=0)

                while slot_time < end_of_day:
                    slots.append({
                        "date": current.strftime("%Y-%m-%d"),
                        "time": slot_time.strftime("%H:%M"),
                        "available": True,  # TODO: Check against Google Calendar
                        "timezone": timezone,
                    })
                    slot_time += timedelta(minutes=30)

            current += timedelta(days=1)

        return slots

    async def create_booking(
        self,
        recruiter_name: str,
        recruiter_email: str,
        company: str,
        date_str: str,
        time_str: str,
        timezone: str,
        duration: int = 30,
        meeting_type: str = "video",
        notes: Optional[str] = None,
    ) -> Dict:
        """
        Create a Google Calendar event with Google Meet link.
        Sends invites to both Rajnish and the recruiter.
        """
        try:
            # Parse datetime
            tz = pytz.timezone(timezone)
            start_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            start_dt = tz.localize(start_dt)
            end_dt = start_dt + timedelta(minutes=duration)

            booking_id = str(uuid.uuid4())[:8].upper()

            # Google Calendar Event
            event_body = {
                "summary": f"Interview: {recruiter_name} ({company}) × Rajnish Kumar",
                "description": (
                    f"Interview scheduled via AI Persona\n\n"
                    f"Recruiter: {recruiter_name} <{recruiter_email}>\n"
                    f"Company: {company}\n"
                    f"Duration: {duration} minutes\n"
                    f"Notes: {notes or 'N/A'}\n\n"
                    f"Booking ID: {booking_id}"
                ),
                "start": {
                    "dateTime": start_dt.isoformat(),
                    "timeZone": timezone,
                },
                "end": {
                    "dateTime": end_dt.isoformat(),
                    "timeZone": timezone,
                },
                "attendees": [
                    {"email": settings.GOOGLE_CALENDAR_EMAIL if hasattr(settings, 'GOOGLE_CALENDAR_EMAIL') else "rk2452003@gmail.com"},
                    {"email": recruiter_email},
                ],
                "conferenceData": {
                    "createRequest": {
                        "requestId": booking_id,
                        "conferenceSolutionKey": {"type": "hangoutsMeet"},
                    }
                },
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "email", "minutes": 60},
                        {"method": "popup", "minutes": 15},
                    ],
                },
            }

            # TODO: Use actual Google Calendar API client
            # For demo, return mock response
            mock_meet_link = f"https://meet.google.com/{booking_id.lower()}-xxxx"
            mock_calendar_link = (
                f"https://calendar.google.com/calendar/event?eid={booking_id}"
            )

            logger.info(f"Booking created: {booking_id} for {recruiter_email}")

            return {
                "booking_id": booking_id,
                "calendar_link": mock_calendar_link,
                "meet_link": mock_meet_link,
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat(),
                "event_body": event_body,
            }

        except Exception as e:
            logger.error(f"Booking creation failed: {e}", exc_info=True)
            raise

    async def exchange_code(self, code: str) -> Dict:
        """Exchange OAuth code for credentials."""
        from google_auth_oauthlib.flow import Flow

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=["https://www.googleapis.com/auth/calendar"],
        )
        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
        flow.fetch_token(code=code)
        return {"status": "ok"}

    async def get_booking(self, booking_id: str) -> Optional[Dict]:
        """Retrieve booking details from storage."""
        # TODO: Implement with Supabase
        return None
