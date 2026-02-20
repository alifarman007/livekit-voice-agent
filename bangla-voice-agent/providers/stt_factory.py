"""
STT Provider Factory
═══════════════════════════════════════════════════
Change STT_PROVIDER in .env to swap:
  google      -> Google Cloud Speech-to-Text (best Bengali)
  azure       -> Azure Speech Services (good Bengali, cheaper)
  deepgram    -> Deepgram Nova-3 (fast, limited Bengali)
  elevenlabs  -> ElevenLabs Scribe (multilingual)
  assemblyai  -> AssemblyAI Universal-2 (good accuracy)
  custom      -> Any custom STT endpoint
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

try:
    from livekit.plugins import azure as azure_plugin
except ImportError:
    azure_plugin = None

try:
    from livekit.plugins import assemblyai as assemblyai_plugin
except ImportError:
    assemblyai_plugin = None

from config import config

logger = logging.getLogger("voice-agent.stt")


def get_stt() -> stt_module.STT:
    """Return the configured STT instance based on .env settings."""

    provider = config.stt_provider.lower()
    language = config.language

    # ─────────────────────────────────────
    # Google Cloud Speech-to-Text
    # Best Bengali (bn-BD) support
    # Requires: GOOGLE_APPLICATION_CREDENTIALS
    # ─────────────────────────────────────
    if provider == "google":
        logger.info(f"🎤 STT: Google Cloud Speech-to-Text (language={language})")
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

    # ─────────────────────────────────────
    # Azure Speech Services
    # Good Bengali (bn-BD), cheaper than Google
    # Requires: AZURE_SPEECH_KEY, AZURE_SPEECH_REGION
    # ─────────────────────────────────────
    elif provider == "azure":
        if azure_plugin is None:
            raise ImportError(
                "Azure STT requires livekit-plugins-azure. "
                "Install: pip install livekit-plugins-azure"
            )
        if not config.azure_speech_key:
            raise ValueError(
                "Azure STT requires AZURE_SPEECH_KEY and AZURE_SPEECH_REGION in .env"
            )
        logger.info(f"🎤 STT: Azure Speech Services (language={language}, region={config.azure_speech_region})")
        return azure_plugin.STT(
            speech_key=config.azure_speech_key,
            speech_region=config.azure_speech_region,
            languages=[language],
        )

    # ─────────────────────────────────────
    # Deepgram Nova-3
    # Fast, but limited Bengali support
    # Requires: DEEPGRAM_API_KEY
    # ─────────────────────────────────────
    elif provider == "deepgram":
        if deepgram_plugin is None:
            raise ImportError(
                "Deepgram STT requires livekit-plugins-deepgram. "
                "Install: pip install livekit-plugins-deepgram"
            )
        logger.info(f"🎤 STT: Deepgram Nova-3 (language={language})")
        return deepgram_plugin.STT(
            api_key=config.deepgram_api_key or None,
            language=language,
            model="nova-3",
        )

    # ─────────────────────────────────────
    # ElevenLabs Scribe
    # Good multilingual, auto language detection
    # Requires: ELEVEN_API_KEY
    # ─────────────────────────────────────
    elif provider == "elevenlabs":
        if elevenlabs_plugin is None:
            raise ImportError(
                "ElevenLabs STT requires livekit-plugins-elevenlabs. "
                "Install: pip install livekit-plugins-elevenlabs"
            )
        lang_code = language.split("-")[0]  # bn-BD -> bn
        logger.info(f"🎤 STT: ElevenLabs Scribe (language={lang_code})")
        return elevenlabs_plugin.STT(
            api_key=config.eleven_api_key or None,
            language_code=lang_code,
        )

    # ─────────────────────────────────────
    # AssemblyAI Universal-2
    # Good accuracy, streaming support
    # Requires: ASSEMBLYAI_API_KEY
    # ─────────────────────────────────────
    elif provider == "assemblyai":
        if assemblyai_plugin is None:
            raise ImportError(
                "AssemblyAI STT requires livekit-plugins-assemblyai. "
                "Install: pip install livekit-plugins-assemblyai"
            )
        logger.info(f"🎤 STT: AssemblyAI Universal-2 (language={language})")
        return assemblyai_plugin.STT(
            api_key=config.assemblyai_api_key or None,
            language=language,
        )

    # ─────────────────────────────────────
    # Custom STT endpoint
    # For self-hosted or local models
    # ─────────────────────────────────────
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
            f"Valid options: google, azure, deepgram, elevenlabs, assemblyai, custom"
        )
