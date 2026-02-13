"""
Appointment Booking Tool
The LLM calls these functions when a caller wants to book, check, or cancel appointments.
Currently returns mock data — connect to your real calendar API later.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from livekit.agents import RunContext, function_tool

logger = logging.getLogger("voice-agent.tools.appointment")

# In-memory store for MVP testing (replace with database/API later)
_appointments: list[dict] = []


@function_tool()
async def check_available_slots(
    context: RunContext,
    date: str,
) -> dict:
    """Check available appointment slots for a given date.

    Args:
        date: The date to check in YYYY-MM-DD format (e.g., "2025-02-15")
    """
    logger.info(f"📅 Checking slots for {date}")

    # Mock available slots — replace with real calendar API
    available_slots = [
        {"time": "10:00 AM", "duration": "30 min"},
        {"time": "11:30 AM", "duration": "30 min"},
        {"time": "2:00 PM", "duration": "30 min"},
        {"time": "3:30 PM", "duration": "30 min"},
        {"time": "5:00 PM", "duration": "30 min"},
    ]

    # Filter out already booked slots
    booked_times = {
        apt["time"] for apt in _appointments if apt["date"] == date
    }
    available = [s for s in available_slots if s["time"] not in booked_times]

    return {
        "date": date,
        "available_slots": available,
        "total_available": len(available),
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
    """Book an appointment for the caller.

    Args:
        caller_name: Full name of the person booking
        phone_number: Contact phone number
        date: Appointment date in YYYY-MM-DD format
        time: Appointment time (e.g., "10:00 AM")
        purpose: Reason for the appointment
    """
    logger.info(f"📅 Booking: {caller_name} on {date} at {time}")

    appointment = {
        "id": f"APT-{len(_appointments) + 1001}",
        "caller_name": caller_name,
        "phone_number": phone_number,
        "date": date,
        "time": time,
        "purpose": purpose,
        "status": "confirmed",
        "created_at": datetime.now().isoformat(),
    }
    _appointments.append(appointment)

    return {
        "success": True,
        "appointment_id": appointment["id"],
        "message": f"Appointment confirmed for {caller_name} on {date} at {time}",
        "details": appointment,
    }


@function_tool()
async def cancel_appointment(
    context: RunContext,
    appointment_id: str,
) -> dict:
    """Cancel an existing appointment.

    Args:
        appointment_id: The appointment ID to cancel (e.g., "APT-1001")
    """
    logger.info(f"📅 Cancelling: {appointment_id}")

    for apt in _appointments:
        if apt["id"] == appointment_id:
            apt["status"] = "cancelled"
            return {
                "success": True,
                "message": f"Appointment {appointment_id} has been cancelled.",
            }

    return {
        "success": False,
        "message": f"Appointment {appointment_id} not found.",
    }


@function_tool()
async def get_next_available(
    context: RunContext,
) -> dict:
    """Get the next available appointment slot from today."""
    logger.info("📅 Finding next available slot")

    today = datetime.now()
    # Check next 7 days
    for i in range(7):
        date = (today + timedelta(days=i)).strftime("%Y-%m-%d")
        booked = {apt["time"] for apt in _appointments if apt["date"] == date}
        all_slots = ["10:00 AM", "11:30 AM", "2:00 PM", "3:30 PM", "5:00 PM"]
        available = [s for s in all_slots if s not in booked]
        if available:
            return {
                "date": date,
                "time": available[0],
                "message": f"Next available: {date} at {available[0]}",
            }

    return {"message": "No available slots in the next 7 days."}
