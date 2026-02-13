"""
Central configuration for the Bangla Voice Agent.
Reads .env and exposes typed config for all providers.
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """All configuration in one place. Change .env to swap providers."""

    # Provider selection
    stt_provider: str = os.getenv("STT_PROVIDER", "google")
    llm_provider: str = os.getenv("LLM_PROVIDER", "gemini")
    tts_provider: str = os.getenv("TTS_PROVIDER", "google")

    # Language & mode
    language: str = os.getenv("LANGUAGE", "bn-BD")
    agent_mode: str = os.getenv("AGENT_MODE", "receptionist")

    # Google / Gemini
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    google_credentials: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Anthropic
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")

    # Groq
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "qwen-qwq-32b")

    # ElevenLabs
    eleven_api_key: str = os.getenv("ELEVEN_API_KEY", "")
    eleven_voice_id: str = os.getenv("ELEVEN_VOICE_ID", "pNInz6obpgDQGcFmaJgB")
    eleven_model: str = os.getenv("ELEVEN_MODEL", "eleven_multilingual_v2")

    # Deepgram
    deepgram_api_key: str = os.getenv("DEEPGRAM_API_KEY", "")

    # Cartesia
    cartesia_api_key: str = os.getenv("CARTESIA_API_KEY", "")

    # Custom endpoints
    custom_stt_url: str = os.getenv("CUSTOM_STT_URL", "http://localhost:8001/stt")
    custom_tts_url: str = os.getenv("CUSTOM_TTS_URL", "http://localhost:8002/tts")
    custom_llm_url: str = os.getenv("CUSTOM_LLM_URL", "http://localhost:8003/v1")

    # Google Cloud TTS voice options
    google_tts_voice: str = os.getenv("GOOGLE_TTS_VOICE", "bn-BD-Wavenet-A")
    google_tts_speaking_rate: float = float(os.getenv("GOOGLE_TTS_SPEAKING_RATE", "1.0"))
    google_tts_pitch: float = float(os.getenv("GOOGLE_TTS_PITCH", "0.0"))

    # LiveKit
    livekit_url: str = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
    livekit_api_key: str = os.getenv("LIVEKIT_API_KEY", "devkey")
    livekit_api_secret: str = os.getenv("LIVEKIT_API_SECRET", "secret")

    def print_config(self):
        """Print active configuration for debugging."""
        print("\n" + "=" * 50)
        print("🎙️  BANGLA VOICE AGENT - Active Config")
        print("=" * 50)
        print(f"  STT Provider : {self.stt_provider}")
        print(f"  LLM Provider : {self.llm_provider}")
        print(f"  TTS Provider : {self.tts_provider}")
        print(f"  Language     : {self.language}")
        print(f"  Agent Mode   : {self.agent_mode}")
        print(f"  LiveKit URL  : {self.livekit_url}")
        print("=" * 50 + "\n")


# Singleton config instance
config = Config()
