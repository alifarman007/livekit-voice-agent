"""
CRM Tool — Google Sheets Integration
The LLM calls these functions to look up and update customer information.
Uses real Google Sheets as a lightweight CRM database.

Sheet structure (first row = headers):
  A: Name | B: Phone | C: Email | D: Company | E: Last Interaction | F: Notes | G: Status
"""

from __future__ import annotations

import logging
from datetime import datetime

import gspread
from google.oauth2 import service_account

from livekit.agents import RunContext, function_tool
from config import config

logger = logging.getLogger("voice-agent.tools.crm")

# Google Sheets setup
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
SHEET_ID = config.google_sheet_id
CREDENTIALS_FILE = config.google_credentials

# Expected column headers (will auto-create if sheet is empty)
HEADERS = ["Name", "Phone", "Email", "Company", "Last Interaction", "Notes", "Status"]


def _get_sheet():
    """Get the Google Sheet worksheet (first sheet)."""
    if not CREDENTIALS_FILE:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not set in .env")
    if not SHEET_ID:
        raise ValueError("GOOGLE_SHEET_ID not set in .env")

    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(SHEET_ID)
    worksheet = spreadsheet.sheet1

    # Auto-setup headers if sheet is empty
    existing = worksheet.row_values(1)
    if not existing:
        worksheet.update("A1:G1", [HEADERS])
        logger.info("📋 Initialized Google Sheet with CRM headers")

    return worksheet


def _normalize_phone(phone: str) -> str:
    """Normalize a phone number by removing spaces, dashes, and country code."""
    phone = phone.replace("+88", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
    # Convert Bengali digits to ASCII
    bn_digits = "০১২৩৪৫৬৭৮৯"
    for i, bn in enumerate(bn_digits):
        phone = phone.replace(bn, str(i))
    return phone


def _find_customer_row(worksheet, phone: str) -> int | None:
    """Find the row number of a customer by phone number. Returns None if not found."""
    phone_normalized = _normalize_phone(phone)
    try:
        all_phones = worksheet.col_values(2)  # Column B = Phone
        for idx, cell_phone in enumerate(all_phones):
            if idx == 0:  # Skip header
                continue
            if _normalize_phone(cell_phone) == phone_normalized:
                return idx + 1  # gspread is 1-indexed
    except Exception:
        pass
    return None


@function_tool()
async def register_customer(
    context: RunContext,
    customer_name: str,
    phone_number: str,
) -> dict:
    """Register a new customer with their name and phone number in the CRM.
    Use this when a caller wants to register or sign up.

    Args:
        customer_name: Full name of the customer
        phone_number: Customer's phone number
    """
    logger.info(f"📋 Registering customer: {customer_name} ({phone_number})")

    try:
        worksheet = _get_sheet()
        phone_clean = _normalize_phone(phone_number)
        today = datetime.now().strftime("%Y-%m-%d")

        # Check if already exists
        row_num = _find_customer_row(worksheet, phone_number)

        if row_num:
            # Update existing record with name
            worksheet.update_cell(row_num, 1, customer_name)  # Name
            worksheet.update_cell(row_num, 5, today)  # Last Interaction
            worksheet.update_cell(row_num, 7, "active")  # Status
            logger.info(f"📋 ✅ Updated existing customer at row {row_num}")
            return {
                "success": True,
                "message": f"{customer_name} ({phone_clean}) updated successfully.",
                "new_registration": False,
            }
        else:
            # Create new customer
            new_row = [
                customer_name,
                phone_clean,
                "",  # Email
                "",  # Company
                today,
                "Registered via phone call",
                "active",
            ]
            worksheet.append_row(new_row)
            logger.info(f"📋 ✅ New customer registered: {customer_name}")
            return {
                "success": True,
                "message": f"{customer_name} ({phone_clean}) registered successfully.",
                "new_registration": True,
            }
    except Exception as e:
        logger.error(f"📋 Registration error: {e}")
        return {
            "success": False,
            "message": f"Registration failed: {str(e)}",
        }


@function_tool()
async def lookup_customer(
    context: RunContext,
    phone_number: str,
) -> dict:
    """Look up a customer by their phone number in the Google Sheets CRM.

    Args:
        phone_number: Customer's phone number
    """
    logger.info(f"🔍 CRM lookup: {phone_number}")

    try:
        worksheet = _get_sheet()
        row_num = _find_customer_row(worksheet, phone_number)

        if row_num:
            row = worksheet.row_values(row_num)
            while len(row) < len(HEADERS):
                row.append("")

            customer = {
                "name": row[0],
                "phone": row[1],
                "email": row[2],
                "company": row[3],
                "last_interaction": row[4],
                "notes": row[5],
                "status": row[6],
            }
            logger.info(f"🔍 Found customer: {customer['name']}")
            return {"found": True, "customer": customer}

        logger.info(f"🔍 No customer found for {phone_number}")
        return {
            "found": False,
            "message": f"No customer found with phone number {phone_number}",
        }
    except Exception as e:
        logger.error(f"🔍 CRM error: {e}")
        return {"found": False, "message": f"CRM lookup error: {str(e)}"}


@function_tool()
async def update_customer_notes(
    context: RunContext,
    phone_number: str,
    notes: str,
) -> dict:
    """Add new notes to a customer's record in the Google Sheets CRM.
    New notes are APPENDED to existing notes — nothing is deleted.
    Creates a new record if the customer is not found.

    Args:
        phone_number: Customer's phone number
        notes: New notes to add to the customer record
    """
    logger.info(f"📝 CRM update: {phone_number}")

    try:
        worksheet = _get_sheet()
        row_num = _find_customer_row(worksheet, phone_number)
        today = datetime.now().strftime("%Y-%m-%d")

        if row_num:
            # ── FIX: APPEND to existing notes instead of overwriting ──
            # This preserves ticket numbers and previous notes
            existing_notes = worksheet.cell(row_num, 6).value or ""
            if existing_notes:
                updated_notes = f"{existing_notes}\n{notes}"
            else:
                updated_notes = notes

            worksheet.update_cell(row_num, 5, today)       # Last Interaction
            worksheet.update_cell(row_num, 6, updated_notes)  # Notes (appended)
            logger.info(f"📝 Appended notes to customer at row {row_num}")
            return {"success": True, "message": "Customer notes updated."}
        else:
            new_row = [
                "",
                _normalize_phone(phone_number),
                "",
                "",
                today,
                notes,
                "new",
            ]
            worksheet.append_row(new_row)
            logger.info(f"📝 Created new customer record")
            return {"success": True, "message": "New customer record created."}
    except Exception as e:
        logger.error(f"📝 CRM update error: {e}")
        return {"success": False, "message": f"CRM update error: {str(e)}"}


@function_tool()
async def create_support_ticket(
    context: RunContext,
    caller_name: str,
    phone_number: str,
    issue_description: str,
    priority: str,
) -> dict:
    """Create a support ticket by adding a row to the Google Sheets CRM and updating notes.

    Args:
        caller_name: Name of the caller
        phone_number: Contact number
        issue_description: Description of the issue
        priority: Priority level: low, medium, or high
    """
    logger.info(f"🎫 Creating ticket for {caller_name}: {priority}")

    try:
        worksheet = _get_sheet()
        today = datetime.now().strftime("%Y-%m-%d")
        ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        row_num = _find_customer_row(worksheet, phone_number)
        ticket_note = f"[{ticket_id}] ({priority}) {issue_description}"

        if row_num:
            existing_notes = worksheet.cell(row_num, 6).value or ""
            new_notes = f"{ticket_note}\n{existing_notes}" if existing_notes else ticket_note
            worksheet.update_cell(row_num, 1, caller_name)
            worksheet.update_cell(row_num, 5, today)
            worksheet.update_cell(row_num, 6, new_notes)
            worksheet.update_cell(row_num, 7, "support")
        else:
            new_row = [
                caller_name,
                _normalize_phone(phone_number),
                "",
                "",
                today,
                ticket_note,
                "support",
            ]
            worksheet.append_row(new_row)

        logger.info(f"🎫 ✅ Ticket created: {ticket_id}")
        return {
            "success": True,
            "ticket": {
                "ticket_id": ticket_id,
                "caller_name": caller_name,
                "phone_number": phone_number,
                "issue": issue_description,
                "priority": priority,
                "status": "open",
                "created_at": datetime.now().isoformat(),
            },
            "message": f"Support ticket {ticket_id} created with {priority} priority.",
        }
    except Exception as e:
        logger.error(f"🎫 Ticket error: {e}")
        return {
            "success": False,
            "message": f"Failed to create ticket: {str(e)}",
        }
