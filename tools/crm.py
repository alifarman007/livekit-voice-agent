"""
CRM Tool
The LLM calls these functions to look up and update customer information.
Currently returns mock data — connect to your real CRM later (HubSpot, Salesforce, etc.).
"""

from __future__ import annotations

import logging
from datetime import datetime

from livekit.agents import RunContext, function_tool

logger = logging.getLogger("voice-agent.tools.crm")

# Mock CRM database for testing
_customers: dict[str, dict] = {
    "01711111111": {
        "name": "রহিম আহমেদ",
        "phone": "01711111111",
        "email": "rahim@example.com",
        "company": "ABC Technologies",
        "last_interaction": "2025-01-15",
        "notes": "Interested in premium plan",
        "status": "active",
    },
    "01722222222": {
        "name": "করিম হোসেন",
        "phone": "01722222222",
        "email": "karim@example.com",
        "company": "XYZ Corp",
        "last_interaction": "2025-02-01",
        "notes": "Requested callback about billing",
        "status": "active",
    },
}


@function_tool()
async def lookup_customer(
    context: RunContext,
    phone_number: str,
) -> dict:
    """Look up a customer by their phone number.

    Args:
        phone_number: Customer's phone number
    """
    logger.info(f"🔍 CRM lookup: {phone_number}")

    # Normalize phone number
    phone = phone_number.replace("+88", "").replace("-", "").replace(" ", "")

    if phone in _customers:
        return {
            "found": True,
            "customer": _customers[phone],
        }

    return {
        "found": False,
        "message": f"No customer found with phone number {phone_number}",
    }


@function_tool()
async def update_customer_notes(
    context: RunContext,
    phone_number: str,
    notes: str,
) -> dict:
    """Update notes for a customer after a call.

    Args:
        phone_number: Customer's phone number
        notes: New notes to add to the customer record
    """
    logger.info(f"📝 CRM update: {phone_number}")

    phone = phone_number.replace("+88", "").replace("-", "").replace(" ", "")

    if phone in _customers:
        _customers[phone]["notes"] = notes
        _customers[phone]["last_interaction"] = datetime.now().strftime("%Y-%m-%d")
        return {"success": True, "message": "Customer notes updated."}

    # Create new customer record
    _customers[phone] = {
        "name": "Unknown",
        "phone": phone,
        "email": "",
        "company": "",
        "last_interaction": datetime.now().strftime("%Y-%m-%d"),
        "notes": notes,
        "status": "new",
    }
    return {"success": True, "message": "New customer record created."}


@function_tool()
async def create_support_ticket(
    context: RunContext,
    caller_name: str,
    phone_number: str,
    issue_description: str,
    priority: str,
) -> dict:
    """Create a support ticket for the caller.

    Args:
        caller_name: Name of the caller
        phone_number: Contact number
        issue_description: Description of the issue
        priority: Priority level: low, medium, or high
    """
    logger.info(f"🎫 Creating ticket for {caller_name}: {priority}")

    ticket = {
        "ticket_id": f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "caller_name": caller_name,
        "phone_number": phone_number,
        "issue": issue_description,
        "priority": priority,
        "status": "open",
        "created_at": datetime.now().isoformat(),
    }

    return {
        "success": True,
        "ticket": ticket,
        "message": f"Support ticket {ticket['ticket_id']} created with {priority} priority.",
    }
