"""
Voice Router — Vapi Webhook Handler
POST /api/v1/voice/webhook    (Vapi events)
POST /api/v1/voice/start-call
GET  /api/v1/voice/config
"""

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
import hmac
import hashlib

from config import settings
from prompts.voice_prompt import VOICE_SYSTEM_PROMPT, VOICE_FIRST_MESSAGE

logger = logging.getLogger(__name__)
router = APIRouter()


class StartCallRequest(BaseModel):
    phone_number: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None


@router.get("/config")
async def get_vapi_config():
    """
    Returns Vapi assistant configuration.
    Used to provision the voice agent.
    """
    return {
        "assistant": {
            "name": "Rajnish Kumar AI Persona",
            "firstMessage": VOICE_FIRST_MESSAGE,
            "model": {
                "provider": "openai",
                "model": "gpt-4o",
                "temperature": 0.2,
                "systemPrompt": VOICE_SYSTEM_PROMPT,
                "maxTokens": 200,  # Keep voice responses short
            },
            "voice": {
                "provider": "elevenlabs",
                "voiceId": settings.ELEVENLABS_VOICE_ID,
                "stability": 0.5,
                "similarityBoost": 0.75,
                "speed": 1.0,
            },
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "en-IN",  # Indian English
                "smartFormat": True,
            },
            "endCallFunctionEnabled": True,
            "hipaaEnabled": False,
            "maxDurationSeconds": 1800,
            "backgroundSound": "off",
            "backchannelingEnabled": True,  # Filler "mm-hmm" sounds
            "responseDelaySeconds": 0.1,
            "llmRequestDelaySeconds": 0.05,
        }
    }


@router.post("/webhook")
async def vapi_webhook(request: Request):
    """
    Handle Vapi webhook events:
    - call-started, call-ended, function-call, status-update
    """
    # Verify Vapi signature
    body = await request.body()
    signature = request.headers.get("x-vapi-signature", "")
    expected = hmac.new(
        settings.VAPI_API_KEY.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()

    # In production, validate: if signature != expected: raise 401

    payload = await request.json()
    event_type = payload.get("message", {}).get("type", "")
    logger.info(f"Vapi event: {event_type}")

    if event_type == "function-call":
        return await handle_function_call(payload)

    if event_type == "end-of-call-report":
        call_id = payload.get("message", {}).get("call", {}).get("id")
        logger.info(f"Call ended: {call_id}")

    return {"status": "ok"}


async def handle_function_call(payload: dict) -> dict:
    """
    Handle tool calls from Vapi (calendar booking, etc.)
    """
    fn_call = payload.get("message", {}).get("functionCall", {})
    fn_name = fn_call.get("name", "")
    fn_params = fn_call.get("parameters", {})

    if fn_name == "book_interview":
        from services.calendar_service import CalendarService
        cal = CalendarService()
        result = await cal.create_booking(**fn_params)
        return {
            "result": (
                f"Interview booked! You'll receive a calendar invite at {fn_params.get('recruiter_email')}. "
                f"Booking ID: {result['booking_id']}. "
                f"Google Meet link: {result['meet_link']}"
            )
        }

    elif fn_name == "get_available_slots":
        from services.calendar_service import CalendarService
        cal = CalendarService()
        slots = await cal.get_free_slots(
            fn_params.get("date_from", ""),
            fn_params.get("date_to", ""),
        )
        available = [s for s in slots if s["available"]][:5]
        slot_text = ", ".join([f"{s['date']} at {s['time']}" for s in available])
        return {"result": f"Available slots: {slot_text}"}

    return {"result": "Function not found"}


@router.post("/start-call")
async def start_outbound_call(req: StartCallRequest):
    """Initiate an outbound Vapi call (optional feature)."""
    if not req.phone_number:
        raise HTTPException(status_code=400, detail="Phone number required")

    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.vapi.ai/call/phone",
            headers={"Authorization": f"Bearer {settings.VAPI_API_KEY}"},
            json={
                "phoneNumberId": settings.VAPI_PHONE_NUMBER_ID,
                "customer": {"number": req.phone_number, "name": req.customer_name},
                "assistantId": "YOUR_ASSISTANT_ID",
            },
        )
    return response.json()
