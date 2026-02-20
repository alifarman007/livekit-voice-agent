"""
STT Provider Factory
"""

from __future__ import annotations

import logging
from livekit.agents import stt as stt_module

from livekit.plugins import google as google_plugin
from livekit.plugins import openai as openai_plugin

try:
    from livekit.plugins import elevenlabs as elevenlabs_plugin
except ImportError:
    elevenlabs_plugin = None

try:
    from livekit.plugins import deepgram as deepgram_plugin
except ImportError:
    deepgram_plugin = None

from config import config

logger = logging.getLogger("voice-agent.stt")


def get_stt() -> stt_module.STT:
    """Return the configured STT instance based on .env settings."""

    provider = config.stt_provider.lower()
    language = config.language

    if provider == "google":
        logger.info(f"🎤 STT: Google Cloud Speech-to-Text (language={language})")
        # Google Cloud STT requires service account JSON, not API key
        creds_file = config.google_credentials
        if not creds_file:
            raise ValueError(
                "Google Cloud STT requires GOOGLE_APPLICATION_CREDENTIALS "
                "pointing to your service account JSON file in .env"
            )
        return google_plugin.STT(
            languages=[language],
            credentials_file=creds_file,
        )

    elif provider == "elevenlabs":
        if elevenlabs_plugin is None:
            raise ImportError("pip install livekit-plugins-elevenlabs")
        lang_code = language.split("-")[0]  # bn-BD -> bn
        logger.info(f"🎤 STT: ElevenLabs Scribe (language={lang_code})")
        return elevenlabs_plugin.STT(
            api_key=config.eleven_api_key or None,
            language_code=lang_code,
        )

    elif provider == "deepgram":
        if deepgram_plugin is None:
            raise ImportError("pip install livekit-plugins-deepgram")
        logger.info(f"🎤 STT: Deepgram Nova-3 (language={language})")
        return deepgram_plugin.STT(
            api_key=config.deepgram_api_key or None,
            language=language,
            model="nova-3",
        )

    elif provider == "custom":
        logger.warning(
            "⚠️  Custom STT not yet implemented. Using Google Cloud STT as fallback."
        )
        return google_plugin.STT(
            languages=[language],
            credentials_file=config.google_credentials,
        )

    else:
        raise ValueError(
            f"Unknown STT_PROVIDER: '{provider}'. "
            f"Valid options: google, elevenlabs, deepgram, custom"
        )
