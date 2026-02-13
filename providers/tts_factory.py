"""
TTS Provider Factory
"""

from __future__ import annotations

import logging
import re
from livekit.agents import tts as tts_module

from livekit.plugins import google as google_plugin
from livekit.plugins import openai as openai_plugin

try:
    from livekit.plugins import elevenlabs as elevenlabs_plugin
except ImportError:
    elevenlabs_plugin = None

try:
    from livekit.plugins import cartesia as cartesia_plugin
except ImportError:
    cartesia_plugin = None

from config import config

logger = logging.getLogger("voice-agent.tts")


def _extract_language_from_voice(voice_name: str, fallback: str) -> str:
    """Extract language code from voice name like 'bn-IN-Chirp3-HD-Kore' -> 'bn-IN'.
    Falls back to the provided fallback language if extraction fails."""
    match = re.match(r'^([a-z]{2}-[A-Z]{2})', voice_name)
    if match:
        return match.group(1)
    return fallback


def get_tts() -> tts_module.TTS:
    """Return the configured TTS instance based on .env settings."""

    provider = config.tts_provider.lower()

    if provider == "google":
        # Auto-detect language from voice name to avoid mismatch
        # (e.g. LANGUAGE=bn-BD but voice=bn-IN-Chirp3-HD-Kore needs bn-IN)
        tts_language = _extract_language_from_voice(
            config.google_tts_voice, config.language
        )
        logger.info(
            f"🔊 TTS: Google Cloud ({config.google_tts_voice}, language={tts_language})"
        )
        creds_file = config.google_credentials
        if not creds_file:
            raise ValueError(
                "Google Cloud TTS requires GOOGLE_APPLICATION_CREDENTIALS "
                "pointing to your service account JSON file in .env"
            )
        return google_plugin.TTS(
            voice_name=config.google_tts_voice,
            language=tts_language,
            speaking_rate=config.google_tts_speaking_rate,
            pitch=config.google_tts_pitch,
            credentials_file=creds_file,
        )

    elif provider == "gemini":
        logger.info("🔊 TTS: Gemini TTS (expressive)")
        return google_plugin.TTS(
            voice_name="Kore",
            api_key=config.google_api_key or None,
        )

    elif provider == "elevenlabs":
        if elevenlabs_plugin is None:
            raise ImportError("pip install livekit-plugins-elevenlabs")
        logger.info(f"🔊 TTS: ElevenLabs ({config.eleven_model})")
        return elevenlabs_plugin.TTS(
            api_key=config.eleven_api_key or None,
            voice_id=config.eleven_voice_id,
            model=config.eleven_model,
            language=config.language.split("-")[0],
        )

    elif provider == "openai":
        logger.info("🔊 TTS: OpenAI (gpt-4o-mini-tts with tone control)")
        return openai_plugin.TTS(
            model="gpt-4o-mini-tts",
            voice="coral",
            instructions="Speak in a warm, friendly, and professional tone. "
            "Match the emotional context of what you are saying.",
        )

    elif provider == "cartesia":
        if cartesia_plugin is None:
            raise ImportError("pip install livekit-plugins-cartesia")
        logger.info("🔊 TTS: Cartesia Sonic-3 (ultra-low latency)")
        return cartesia_plugin.TTS(
            api_key=config.cartesia_api_key or None,
            model="sonic-3",
            language=config.language.split("-")[0],
        )

    elif provider == "custom":
        logger.warning(
            "⚠️  Custom TTS not yet implemented. Using Google Cloud TTS as fallback."
        )
        tts_language = _extract_language_from_voice(
            config.google_tts_voice, config.language
        )
        return google_plugin.TTS(
            voice_name=config.google_tts_voice,
            language=tts_language,
            credentials_file=config.google_credentials,
        )

    else:
        raise ValueError(
            f"Unknown TTS_PROVIDER: '{provider}'. "
            f"Valid options: google, gemini, elevenlabs, openai, cartesia, custom"
        )