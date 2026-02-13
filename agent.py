"""
Bangla Voice Agent — Main Entry Point
=====================================
A modular, config-driven voice agent built on LiveKit Agents.
Everything is swappable via .env — STT, LLM, TTS, telephony, language, and prompts.

Usage:
  Console mode (mic/speaker):  python agent.py console
  Dev mode (browser):          python agent.py dev
  Production:                  python agent.py start

All providers, language, and agent behavior are controlled by .env
"""

from __future__ import annotations

import logging

from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    RunContext,
)
from livekit.plugins import silero

# === IMPORTANT: All plugins MUST be imported at top level (main thread) ===
# LiveKit requires plugin registration on the main thread.
# Import ALL plugins here even if not currently active — only the one
# selected in .env will actually be used at runtime.
from livekit.plugins import google  # Google Cloud STT/TTS + Gemini LLM
from livekit.plugins import openai  # OpenAI + Groq (via base_url)

# Optional plugins — import with try/except so missing ones don't crash
try:
    from livekit.plugins import elevenlabs
except ImportError:
    elevenlabs = None

try:
    from livekit.plugins import anthropic
except ImportError:
    anthropic = None

try:
    from livekit.plugins import cartesia
except ImportError:
    cartesia = None

try:
    from livekit.plugins import deepgram
except ImportError:
    deepgram = None

try:
    from livekit.plugins import turn_detector
except ImportError:
    turn_detector = None

from config import config
from providers import get_stt, get_llm, get_tts
from prompts import get_prompt

# Import all function tools so they're registered
from tools.appointment import (
    check_available_slots,
    book_appointment,
    cancel_appointment,
    get_next_available,
)
from tools.crm import (
    lookup_customer,
    update_customer_notes,
    create_support_ticket,
)
from tools.transfer import (
    transfer_to_department,
    escalate_to_human,
    end_call,
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voice-agent")


class BanglaVoiceAgent(Agent):
    """
    The main voice agent. Configured entirely by .env variables.

    To change behavior:
      - STT_PROVIDER → swap speech recognition
      - LLM_PROVIDER → swap the brain
      - TTS_PROVIDER → swap the voice
      - AGENT_MODE   → swap personality (receptionist/appointment/support)
      - LANGUAGE      → swap language
    """

    def __init__(self) -> None:
        super().__init__(
            instructions=get_prompt(
                mode=config.agent_mode,
                company_name="আমাদের কোম্পানি",  # Change to your company name
            ),
        )


# Create the agent server
server = AgentServer()


@server.rtc_session()
async def entrypoint(ctx: JobContext):
    """Entry point for each voice session."""

    # Print active config on startup
    config.print_config()

    # Build the session with configured providers
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=get_stt(),
        llm=get_llm(),
        tts=get_tts(),
        # Turn detection for natural conversation flow
        # turn_detector=turn_detector.EOUModel(),  # Uncomment after installing
    )

    # Connect to the room
    await ctx.connect()

    # Start the agent session
    await session.start(
        room=ctx.room,
        agent=BanglaVoiceAgent(),
    )

    # Generate initial greeting
    await session.generate_reply(
        instructions="Greet the caller warmly in Bengali. Introduce yourself and ask how you can help."
    )

    logger.info("🎙️ Agent session started — waiting for caller...")


if __name__ == "__main__":
    from livekit.agents import cli

    cli.run_app(server)
