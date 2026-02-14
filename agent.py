"""
Bangla Voice Agent — Main Entry Point
=====================================
Usage:
  Console mode (mic/speaker):  python agent.py console
  Room mode (dev/playground):  python agent.py dev
  Production:                  python agent.py start
"""

from __future__ import annotations

import asyncio
import logging

from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    AudioConfig,
    BackgroundAudioPlayer,
    BuiltinAudioClip,
    JobContext,
    RunContext,
    UserStateChangedEvent,
    UserInputTranscribedEvent,
)
from livekit.plugins import silero

# === All plugins MUST be imported at top level (main thread) ===
from livekit.plugins import google
from livekit.plugins import openai

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

# Import all function tools
from tools.appointment import (
    check_available_slots,
    book_appointment,
    cancel_appointment,
    get_next_available,
)
from tools.crm import (
    register_customer,
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

# ALL tools — passed to Agent so the LLM can actually call them
ALL_TOOLS = [
    register_customer,
    lookup_customer,
    update_customer_notes,
    create_support_ticket,
    check_available_slots,
    book_appointment,
    cancel_appointment,
    get_next_available,
    transfer_to_department,
    escalate_to_human,
    end_call,
]

# ═══════════════════════════════════════════════════════
# BACKGROUND AUDIO CLIPS (from LiveKit built-in library)
# ═══════════════════════════════════════════════════════
AUDIO_CLIPS = {
    "office": BuiltinAudioClip.OFFICE_AMBIENCE,
    "city": BuiltinAudioClip.CITY_AMBIENCE,
    "forest": BuiltinAudioClip.FOREST_AMBIENCE,
    "crowd": BuiltinAudioClip.CROWDED_ROOM,
    "typing": BuiltinAudioClip.KEYBOARD_TYPING,
    "typing2": BuiltinAudioClip.KEYBOARD_TYPING2,
    "hold_music": BuiltinAudioClip.HOLD_MUSIC,
}


def _build_background_audio() -> BackgroundAudioPlayer | None:
    """Build BackgroundAudioPlayer from .env config. Returns None if disabled."""
    if not config.background_audio_enabled:
        logger.info("🔇 Background audio: DISABLED")
        return None

    # Ambient sound (loops continuously)
    ambient_clip = AUDIO_CLIPS.get(config.background_audio_type)
    ambient = None
    if ambient_clip:
        ambient = AudioConfig(
            source=ambient_clip,
            volume=config.background_audio_volume,
        )
        logger.info(
            f"🔊 Background audio: {config.background_audio_type} "
            f"(volume: {config.background_audio_volume})"
        )

    # Thinking sound (plays while agent is processing)
    thinking_clip = AUDIO_CLIPS.get(config.thinking_sound_type)
    thinking = None
    if config.thinking_sound_enabled and thinking_clip:
        thinking = AudioConfig(
            source=thinking_clip,
            volume=config.thinking_sound_volume,
        )
        logger.info(
            f"💭 Thinking sound: {config.thinking_sound_type} "
            f"(volume: {config.thinking_sound_volume})"
        )

    return BackgroundAudioPlayer(
        ambient_sound=ambient,
        thinking_sound=thinking,
    )


class BanglaVoiceAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=get_prompt(
                mode=config.agent_mode,
                company_name="আমাদের কোম্পানি",  # ← Change to your company name
            ),
            tools=ALL_TOOLS,
        )


server = AgentServer()


@server.rtc_session()
async def entrypoint(ctx: JobContext):
    config.print_config()

    # ═══════════════════════════════════════════════════════
    # SILENCE HANDLING — makes the agent behave like a human
    # ═══════════════════════════════════════════════════════

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=get_stt(),
        llm=get_llm(),
        tts=get_tts(),
        user_away_timeout=10.0,  # 10 seconds of silence = nudge
    )

    # Track how many times we've nudged a silent caller
    nudge_count = 0

    # Define what Nusrat says during silence — like a real human
    NUDGE_PROMPTS = [
        # Nudge 1: Gentle check (like "hello? are you there?")
        "কলার চুপ আছে। তুমি মানুষের মতো স্বাভাবিকভাবে বলো: 'হ্যালো? বলুন, আমি শুনছি।' — শুধু এটুকুই বলো, বেশি কিছু না।",

        # Nudge 2: A bit more concerned
        "কলার এখনো চুপ। বলো: 'আপনি কি শুনতে পাচ্ছেন? আমি আপনার কথা শুনতে পাচ্ছি না।' — শুধু এটুকুই।",

        # Nudge 3: Polite goodbye
        "কলার উত্তর দিচ্ছে না। ভদ্রভাবে বিদায় নাও: 'ঠিক আছে, মনে হচ্ছে লাইনে সমস্যা হচ্ছে। আপনি আবার কল দিবেন। আসসালামু আলাইকুম।' — তারপর end_call টুল কল করো।",
    ]

    # Capture the running event loop BEFORE callbacks fire
    # (Fixes asyncio crash on Windows Python 3.11+)
    loop = asyncio.get_running_loop()

    @session.on("user_state_changed")
    def _on_user_state(ev: UserStateChangedEvent):
        """Fires when user goes silent (state: 'away') or starts speaking again."""
        nonlocal nudge_count

        if ev.new_state == "away":
            # User has been silent — speak up like a human would
            idx = min(nudge_count, len(NUDGE_PROMPTS) - 1)
            prompt = NUDGE_PROMPTS[idx]
            nudge_count += 1
            logger.info(f"🔇 Silence detected — nudge #{nudge_count}")
            loop.call_soon(
                lambda p=prompt: loop.create_task(
                    session.generate_reply(instructions=p)
                )
            )

    @session.on("user_input_transcribed")
    def _on_user_spoke(ev: UserInputTranscribedEvent):
        """Reset silence counter whenever the user actually says something."""
        nonlocal nudge_count
        if nudge_count > 0:
            logger.info(f"🔊 User spoke again — resetting silence counter")
            nudge_count = 0

    # Connect and start
    await ctx.connect()

    await session.start(
        room=ctx.room,
        agent=BanglaVoiceAgent(),
    )

    # ═══════════════════════════════════════════════════════
    # BACKGROUND AUDIO — office ambience + thinking sounds
    # Only works in room mode (dev/start), NOT console mode
    # ═══════════════════════════════════════════════════════
    bg_audio = _build_background_audio()
    if bg_audio:
        await bg_audio.start(room=ctx.room, agent_session=session)
        logger.info("🔊 Background audio started")

    # First greeting — always Islamic salam
    await session.generate_reply(
        instructions="আসসালামু আলাইকুম বলে কলারকে সালাম দাও। নিজের পরিচয় দাও — তুমি নুসরাত, এই কোম্পানির রিসেপশনিস্ট। জিজ্ঞেস করো কিভাবে সাহায্য করতে পারো। ২ লাইনের বেশি বলো না।"
    )

    logger.info("🎙️ Agent session started — silence monitor active")


if __name__ == "__main__":
    from livekit.agents import cli

    cli.run_app(server)
