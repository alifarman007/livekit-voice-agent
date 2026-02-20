"""
Agent Prompts — System instructions for different agent modes.
Each prompt defines the agent's personality, language, capabilities, and rules.
"""

from datetime import datetime

from prompts.receptionist import RECEPTIONIST_PROMPT
from prompts.appointment import APPOINTMENT_PROMPT
from prompts.support import SUPPORT_PROMPT

PROMPTS = {
    "receptionist": RECEPTIONIST_PROMPT,
    "appointment": APPOINTMENT_PROMPT,
    "support": SUPPORT_PROMPT,
}


def get_prompt(mode: str, company_name: str = "আমাদের কোম্পানি") -> str:
    """Get the system prompt for the given agent mode.

    Args:
        mode: Agent mode from .env (receptionist, appointment, support)
        company_name: Company name to insert into prompts
    """
    if mode not in PROMPTS:
        raise ValueError(
            f"Unknown AGENT_MODE: '{mode}'. Valid options: {list(PROMPTS.keys())}"
        )

    # Inject today's date so the LLM always knows the current date
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")  # e.g. 2026-02-21
    today_bangla = today.strftime("%d/%m/%Y")  # e.g. 21/02/2026

    return PROMPTS[mode].format(
        company_name=company_name,
        today_date=today_str,
        today_date_bangla=today_bangla,
    )
