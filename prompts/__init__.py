"""
Agent Prompts — System instructions for different agent modes.
Each prompt defines the agent's personality, language, capabilities, and rules.
"""

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

    return PROMPTS[mode].format(company_name=company_name)
