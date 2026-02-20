"""
TTS Provider Factory
═══════════════════════════════════════════════════
Change TTS_PROVIDER in .env to swap:
  google      -> Google Cloud Chirp3-HD (good Bengali, cheapest)
  gemini      -> Gemini TTS (expressive, experimental)
  azure       -> Azure Neural TTS (dedicated bn-BD voice)
  elevenlabs  -> ElevenLabs (best quality, expensive)
  openai      -> OpenAI TTS (tone control, limited Bengali)
  cartesia    -> Cartesia Sonic-3 (ultra-low latency)
  custom      -> Any custom TTS endpoint
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

try:
    from livekit.plugins import azure as azure_plugin
except ImportError:
    azure_plugin = None

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

    # ─────────────────────────────────────
    # Google Cloud TTS (Chirp3-HD)
    # Good Bengali voice, cheapest option (~$4/1M chars)
    # Requires: GOOGLE_APPLICATION_CREDENTIALS
    # ─────────────────────────────────────
    if provider == "google":
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

    # ─────────────────────────────────────
    # Gemini TTS (experimental, expressive)
    # Requires: GOOGLE_API_KEY
    # ─────────────────────────────────────
    elif provider == "gemini":
        logger.info("🔊 TTS: Gemini TTS (expressive)")
        return google_plugin.TTS(
            voice_name="Kore",
            api_key=config.google_api_key or None,
        )

    # ─────────────────────────────────────
    # Azure Neural TTS
    # Dedicated Bengali voices (bn-BD-NabanitaNeural, bn-BD-PradeepNeural)
    # Requires: AZURE_SPEECH_KEY, AZURE_SPEECH_REGION
    # ─────────────────────────────────────
    elif provider == "azure":
        if azure_plugin is None:
            raise ImportError(
                "Azure TTS requires livekit-plugins-azure. "
                "Install: pip install livekit-plugins-azure"
            )
        if not config.azure_speech_key:
            raise ValueError(
                "Azure TTS requires AZURE_SPEECH_KEY and AZURE_SPEECH_REGION in .env"
            )
        logger.info(
            f"🔊 TTS: Azure Neural ({config.azure_tts_voice}, "
            f"region={config.azure_speech_region})"
        )
        return azure_plugin.TTS(
            speech_key=config.azure_speech_key,
            speech_region=config.azure_speech_region,
            voice=config.azure_tts_voice,
        )

    # ─────────────────────────────────────
    # ElevenLabs
    # Best voice quality, expensive (~$120/1M chars)
    # Requires: ELEVEN_API_KEY
    # ─────────────────────────────────────
    elif provider == "elevenlabs":
        if elevenlabs_plugin is None:
            raise ImportError(
                "ElevenLabs TTS requires livekit-plugins-elevenlabs. "
                "Install: pip install livekit-plugins-elevenlabs"
            )
        # ElevenLabs uses ISO 639-3 codes: bn -> ben
        LANG_MAP = {"bn": "ben", "en": "eng", "hi": "hin", "ar": "ara", "ur": "urd"}
        lang_short = config.language.split("-")[0]
        lang_code = LANG_MAP.get(lang_short, lang_short)
        logger.info(
            f"🔊 TTS: ElevenLabs ({config.eleven_model}, "
            f"voice={config.eleven_voice_id}, lang={lang_code})"
        )
        return elevenlabs_plugin.TTS(
            api_key=config.eleven_api_key or None,
            voice_id=config.eleven_voice_id,
            model=config.eleven_model,
            language=lang_code,
        )

    # ─────────────────────────────────────
    # OpenAI TTS
    # Tone-controlled, limited Bengali
    # Requires: OPENAI_API_KEY
    # ─────────────────────────────────────
    elif provider == "openai":
        logger.info("🔊 TTS: OpenAI (gpt-4o-mini-tts with tone control)")
        return openai_plugin.TTS(
            model="gpt-4o-mini-tts",
            voice="coral",
            instructions="Speak in a warm, friendly, and professional tone. "
            "Match the emotional context of what you are saying.",
        )

    # ─────────────────────────────────────
    # Cartesia Sonic-3
    # Ultra-low latency, limited Bengali
    # Requires: CARTESIA_API_KEY
    # ─────────────────────────────────────
    elif provider == "cartesia":
        if cartesia_plugin is None:
            raise ImportError(
                "Cartesia TTS requires livekit-plugins-cartesia. "
                "Install: pip install livekit-plugins-cartesia"
            )
        logger.info("🔊 TTS: Cartesia Sonic-3 (ultra-low latency)")
        return cartesia_plugin.TTS(
            api_key=config.cartesia_api_key or None,
            model="sonic-3",
            language=config.language.split("-")[0],
        )

    # ─────────────────────────────────────
    # Custom TTS endpoint
    # For self-hosted or local models
    # ─────────────────────────────────────
    elif provider == "custom":
        logger.warning(
            "⚠️  Custom TTS not yet implemented. Using Google Cloud TTS as fallback."
        )
        return google_plugin.TTS(
            voice_name=config.google_tts_voice,
            language=config.language,
            credentials_file=config.google_credentials,
        )

    else:
        raise ValueError(
            f"Unknown TTS_PROVIDER: '{provider}'. "
            f"Valid options: google, gemini, azure, elevenlabs, openai, cartesia, custom"
        )
