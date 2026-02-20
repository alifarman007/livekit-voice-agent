"""
Appointment Booking Tool — Google Calendar Integration
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from google.oauth2 import service_account
from googleapiclient.discovery import build

from livekit.agents import RunContext, function_tool
from config import config

logger = logging.getLogger("voice-agent.tools.appointment")

SCOPES = ["https://www.googleapis.com/auth/calendar"]
CALENDAR_ID = config.google_calendar_id
CREDENTIALS_FILE = config.google_credentials
TIMEZONE = "Asia/Dhaka"

BUSINESS_START_HOUR = 9
BUSINESS_END_HOUR = 17
SLOT_DURATION_MINUTES = 30


def _format_time(dt: datetime) -> str:
    """Format time in 12-hour format. Works on Windows and Linux."""
    hour = dt.hour % 12
    if hour == 0:
        hour = 12
    minute = str(dt.minute).zfill(2)
    ampm = "AM" if dt.hour < 12 else "PM"
    return f"{hour}:{minute} {ampm}"


def _get_calendar_service():
    if not CREDENTIALS_FILE:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not set in .env")
    if not CALENDAR_ID:
        raise ValueError("GOOGLE_CALENDAR_ID not set in .env")

    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    return build("calendar", "v3", credentials=credentials, cache_discovery=False)


def _get_busy_times(service, date_str: str) -> list[dict]:
    date = datetime.strptime(date_str, "%Y-%m-%d")
    time_min = date.replace(hour=0, minute=0, second=0).isoformat() + "+06:00"
    time_max = date.replace(hour=23, minute=59, second=59).isoformat() + "+06:00"

    body = {
        "timeMin": time_min,
        "timeMax": time_max,
        "timeZone": TIMEZONE,
        "items": [{"id": CALENDAR_ID}],
    }
    result = service.freebusy().query(body=body).execute()
    return result["calendars"][CALENDAR_ID]["busy"]


def _generate_all_slots(date_str: str) -> list[dict]:
    date = datetime.strptime(date_str, "%Y-%m-%d")
    slots = []
    current = date.replace(hour=BUSINESS_START_HOUR, minute=0, second=0)
    end = date.replace(hour=BUSINESS_END_HOUR, minute=0, second=0)

    while current + timedelta(minutes=SLOT_DURATION_MINUTES) <= end:
        slot_end = current + timedelta(minutes=SLOT_DURATION_MINUTES)
        slots.append({
            "start": current,
            "end": slot_end,
            "time_display": _format_time(current),
            "duration": f"{SLOT_DURATION_MINUTES} min",
        })
        current = slot_end

    return slots


def _is_slot_available(slot: dict, busy_times: list[dict]) -> bool:
    slot_start = slot["start"]
    slot_end = slot["end"]

    for busy in busy_times:
        busy_start_str = busy["start"]
        busy_end_str = busy["end"]

        if busy_start_str.endswith("Z"):
            busy_start = datetime.fromisoformat(busy_start_str.replace("Z", "+00:00"))
            busy_end = datetime.fromisoformat(busy_end_str.replace("Z", "+00:00"))
            busy_start = busy_start.replace(tzinfo=None) + timedelta(hours=6)
            busy_end = busy_end.replace(tzinfo=None) + timedelta(hours=6)
        else:
            # Remove timezone info for comparison
            try:
                busy_start = datetime.fromisoformat(busy_start_str)
                busy_end = datetime.fromisoformat(busy_end_str)
                if busy_start.tzinfo:
                    busy_start = busy_start.replace(tzinfo=None)
                    busy_end = busy_end.replace(tzinfo=None)
            except Exception:
                continue

        if slot_start < busy_end and slot_end > busy_start:
            return False
    return True


@function_tool()
async def check_available_slots(
    context: RunContext,
    date: str,
) -> dict:
    """Check available appointment slots for a given date from Google Calendar.

    Args:
        date: The date to check in YYYY-MM-DD format (e.g., "2026-02-15")
    """
    logger.info(f"📅 Checking Google Calendar slots for {date}")

    try:
        service = _get_calendar_service()
        busy_times = _get_busy_times(service, date)
        all_slots = _generate_all_slots(date)

        available = [
            {"time": s["time_display"], "duration": s["duration"]}
            for s in all_slots
            if _is_slot_available(s, busy_times)
        ]

        logger.info(f"📅 Found {len(available)} available slots on {date}")

        return {
            "date": date,
            "available_slots": available,
            "total_available": len(available),
        }
    except Exception as e:
        logger.error(f"📅 Calendar error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "date": date,
            "error": str(e),
            "available_slots": [],
            "total_available": 0,
        }


@function_tool()
async def book_appointment(
    context: RunContext,
    caller_name: str,
    phone_number: str,
    date: str,
    time: str,
    purpose: str,
) -> dict:
    """Book an appointment by creating a Google Calendar event.

    Args:
        caller_name: Full name of the person booking
        phone_number: Contact phone number
        date: Appointment date in YYYY-MM-DD format
        time: Appointment time (e.g., "10:00 AM")
        purpose: Reason for the appointment
    """
    logger.info(f"📅 Booking: {caller_name} on {date} at {time}")

    try:
        service = _get_calendar_service()

        time_clean = time.strip().upper()
        parsed_time = None
        for fmt in ["%I:%M %p", "%I:%M%p", "%H:%M"]:
            try:
                parsed_time = datetime.strptime(time_clean, fmt)
                break
            except ValueError:
                continue

        if not parsed_time:
            return {"success": False, "message": f"Could not parse time: {time}"}

        date_obj = datetime.strptime(date, "%Y-%m-%d")
        start_dt = date_obj.replace(
            hour=parsed_time.hour, minute=parsed_time.minute, second=0
        )
        end_dt = start_dt + timedelta(minutes=SLOT_DURATION_MINUTES)

        event = {
            "summary": f"Appointment: {caller_name}",
            "description": (
                f"Name: {caller_name}\n"
                f"Phone: {phone_number}\n"
                f"Purpose: {purpose}\n"
                f"Booked via: Bangla Voice Agent"
            ),
            "start": {
                "dateTime": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                "timeZone": TIMEZONE,
            },
            "end": {
                "dateTime": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                "timeZone": TIMEZONE,
            },
            "reminders": {
                "useDefault": False,
                "overrides": [{"method": "popup", "minutes": 30}],
            },
        }

        created_event = (
            service.events()
            .insert(calendarId=CALENDAR_ID, body=event)
            .execute()
        )

        event_id = created_event.get("id", "unknown")
        logger.info(f"📅 ✅ Event created: {event_id}")

        return {
            "success": True,
            "appointment_id": event_id,
            "message": f"Appointment confirmed for {caller_name} on {date} at {time}",
            "details": {
                "caller_name": caller_name,
                "phone_number": phone_number,
                "date": date,
                "time": time,
                "purpose": purpose,
            },
        }
    except Exception as e:
        logger.error(f"📅 Booking error: {e}")
        return {"success": False, "message": f"Failed to book: {str(e)}"}


@function_tool()
async def cancel_appointment(
    context: RunContext,
    caller_name: str,
    date: str,
) -> dict:
    """Cancel an existing appointment by searching for it by caller name and date.

    Args:
        caller_name: Name of the person whose appointment to cancel
        date: The appointment date in YYYY-MM-DD format (e.g., "2026-02-16")
    """
    logger.info(f"📅 Cancelling appointment for {caller_name} on {date}")

    try:
        service = _get_calendar_service()

        # Search for events on that date matching the caller name
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        time_min = date_obj.replace(hour=0, minute=0, second=0).isoformat() + "+06:00"
        time_max = date_obj.replace(hour=23, minute=59, second=59).isoformat() + "+06:00"

        events_result = (
            service.events()
            .list(
                calendarId=CALENDAR_ID,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])

        # Find matching event by caller name (case-insensitive, partial match)
        matched = None
        for event in events:
            summary = event.get("summary", "").lower()
            description = event.get("description", "").lower()
            name_lower = caller_name.lower()

            if name_lower in summary or name_lower in description:
                matched = event
                break

        if not matched:
            logger.warning(f"📅 No appointment found for {caller_name} on {date}")
            return {
                "success": False,
                "message": f"কোনো অ্যাপয়েন্টমেন্ট পাওয়া যায়নি {caller_name}-এর জন্য {date} তারিখে।",
            }

        # Delete the matched event
        event_id = matched["id"]
        event_time = matched.get("start", {}).get("dateTime", "unknown")
        service.events().delete(
            calendarId=CALENDAR_ID, eventId=event_id
        ).execute()

        logger.info(f"📅 ✅ Event cancelled: {event_id} ({matched.get('summary', '')})")
        return {
            "success": True,
            "message": f"{caller_name}-এর {date} তারিখের অ্যাপয়েন্টমেন্ট বাতিল করা হয়েছে।",
            "cancelled_event": matched.get("summary", ""),
        }
    except Exception as e:
        logger.error(f"📅 Cancel error: {e}")
        return {"success": False, "message": f"বাতিল করতে সমস্যা হয়েছে: {str(e)}"}


@function_tool()
async def get_next_available(
    context: RunContext,
) -> dict:
    """Get the next available appointment slot from Google Calendar starting today."""
    logger.info("📅 Finding next available slot")

    try:
        service = _get_calendar_service()
        today = datetime.now()

        for i in range(7):
            date = today + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            busy_times = _get_busy_times(service, date_str)
            all_slots = _generate_all_slots(date_str)

            if i == 0:
                all_slots = [s for s in all_slots if s["start"] > today]

            for slot in all_slots:
                if _is_slot_available(slot, busy_times):
                    return {
                        "date": date_str,
                        "time": slot["time_display"],
                        "message": f"Next available: {date_str} at {slot['time_display']}",
                    }

        return {"message": "No available slots in the next 7 days."}
    except Exception as e:
        logger.error(f"📅 Search error: {e}")
        return {"message": f"Error: {str(e)}"}
