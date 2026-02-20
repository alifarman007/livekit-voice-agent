"""
Call Transfer Tool
Handles call transfers and escalation to human agents.
For MVP: logs the transfer intent. In production: connects to SIP/telephony.
"""

from __future__ import annotations

import logging
from datetime import datetime

from livekit.agents import RunContext, function_tool

logger = logging.getLogger("voice-agent.tools.transfer")


@function_tool()
async def transfer_to_department(
    context: RunContext,
    department: str,
    reason: str,
) -> dict:
    """Transfer the call to a specific department.

    Args:
        department: Department to transfer to (e.g., "sales", "support", "billing", "manager")
        reason: Reason for the transfer
    """
    logger.info(f"📞 Transfer requested → {department}: {reason}")

    # In production, this would initiate a SIP transfer via LiveKit's telephony
    # For MVP, we log and confirm
    return {
        "success": True,
        "message": f"Transferring to {department} department. Reason: {reason}",
        "transfer_id": f"TRF-{datetime.now().strftime('%H%M%S')}",
        # In production, add:
        # "sip_target": "sip:sales@your-pbx.com"
    }


@function_tool()
async def escalate_to_human(
    context: RunContext,
    urgency: str,
    summary: str,
) -> dict:
    """Escalate the call to a human agent when the AI cannot resolve the issue.

    Args:
        urgency: Urgency level: normal or urgent
        summary: Brief summary of the conversation so far for the human agent
    """
    logger.info(f"🚨 Escalation ({urgency}): {summary}")

    return {
        "success": True,
        "message": "Connecting you with a human agent now. Please hold.",
        "estimated_wait": "2 minutes",
        "summary_forwarded": True,
    }


@function_tool()
async def end_call(
    context: RunContext,
    reason: str,
    call_summary: str,
) -> dict:
    """End the current call gracefully with a summary.
    Call this when the caller says goodbye, wants to hang up, or the conversation is complete.

    Args:
        reason: Why the call is ending (e.g., "completed", "caller_request", "issue_resolved")
        call_summary: Brief summary of what was discussed and any actions taken
    """
    logger.info(f"📞 Call ending: {reason}")
    logger.info(f"📞 Call summary: {call_summary}")

    # ─────────────────────────────────────────────────────
    # PRODUCTION: When SIP trunk is connected, uncomment
    # the lines below to actually disconnect the call:
    #
    # import asyncio
    # session = context.session
    # async def _delayed_disconnect():
    #     await asyncio.sleep(2)  # Let goodbye audio finish
    #     await session.aclose()
    # asyncio.ensure_future(_delayed_disconnect())
    # ─────────────────────────────────────────────────────

    return {
        "success": True,
        "reason": reason,
        "summary": call_summary,
        "timestamp": datetime.now().isoformat(),
    }
