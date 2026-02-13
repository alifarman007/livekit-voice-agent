"""
LLM Provider Factory
Change LLM_PROVIDER in .env to swap:
  gemini    -> Google Gemini (free tier 500 req/day)
  openai    -> OpenAI GPT models (requires OPENAI_API_KEY)
  anthropic -> Claude models (requires ANTHROPIC_API_KEY)
  groq      -> Groq ultra-fast inference (requires GROQ_API_KEY)
  custom    -> Any OpenAI-compatible endpoint
"""

from __future__ import annotations

import logging
from livekit.agents import llm as llm_module

# All plugin imports at top level (required by LiveKit)
from livekit.plugins import google as google_plugin
from livekit.plugins import openai as openai_plugin

try:
    from livekit.plugins import anthropic as anthropic_plugin
except ImportError:
    anthropic_plugin = None

from config import config

logger = logging.getLogger("voice-agent.llm")


def get_llm() -> llm_module.LLM:
    """Return the configured LLM instance based on .env settings."""

    provider = config.llm_provider.lower()

    if provider == "gemini":
        logger.info(f"🧠 LLM: Google Gemini ({config.gemini_model})")
        return google_plugin.LLM(
            model=config.gemini_model,
            api_key=config.google_api_key or None,
        )

    elif provider == "openai":
        logger.info(f"🧠 LLM: OpenAI ({config.openai_model})")
        return openai_plugin.LLM(
            model=config.openai_model,
            api_key=config.openai_api_key or None,
        )

    elif provider == "anthropic":
        if anthropic_plugin is None:
            raise ImportError("pip install livekit-plugins-anthropic")
        logger.info(f"🧠 LLM: Anthropic Claude ({config.anthropic_model})")
        return anthropic_plugin.LLM(
            model=config.anthropic_model,
            api_key=config.anthropic_api_key or None,
        )

    elif provider == "groq":
        logger.info(f"🧠 LLM: Groq ({config.groq_model})")
        return openai_plugin.LLM(
            model=config.groq_model,
            api_key=config.groq_api_key or None,
            base_url="https://api.groq.com/openai/v1",
        )

    elif provider == "custom":
        logger.info(f"🧠 LLM: Custom endpoint ({config.custom_llm_url})")
        return openai_plugin.LLM(
            model="default",
            api_key="not-needed",
            base_url=config.custom_llm_url,
        )

    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER: '{provider}'. "
            f"Valid options: gemini, openai, anthropic, groq, custom"
        )
