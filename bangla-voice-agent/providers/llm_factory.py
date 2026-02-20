"""
LLM Provider Factory
═══════════════════════════════════════════════════
Change LLM_PROVIDER in .env to swap:
  gemini    -> Google Gemini (best Bengali, cheapest)
  openai    -> OpenAI GPT models
  anthropic -> Anthropic Claude models
  groq      -> Groq ultra-fast inference
  deepseek  -> DeepSeek (excellent Bengali, very cheap)
  custom    -> Any OpenAI-compatible API endpoint
              (Ollama, vLLM, LM Studio, Together AI, Fireworks, etc.)
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

    # ─────────────────────────────────────
    # Google Gemini
    # Best Bengali understanding, cheapest
    # Requires: GOOGLE_API_KEY
    # ─────────────────────────────────────
    if provider == "gemini":
        logger.info(f"🧠 LLM: Google Gemini ({config.gemini_model})")
        return google_plugin.LLM(
            model=config.gemini_model,
            api_key=config.google_api_key or None,
        )

    # ─────────────────────────────────────
    # OpenAI GPT
    # Strong Bengali, reliable
    # Requires: OPENAI_API_KEY
    # ─────────────────────────────────────
    elif provider == "openai":
        logger.info(f"🧠 LLM: OpenAI ({config.openai_model})")
        return openai_plugin.LLM(
            model=config.openai_model,
            api_key=config.openai_api_key or None,
        )

    # ─────────────────────────────────────
    # Anthropic Claude
    # Strong Bengali, great reasoning
    # Requires: ANTHROPIC_API_KEY
    # ─────────────────────────────────────
    elif provider == "anthropic":
        if anthropic_plugin is None:
            raise ImportError(
                "Anthropic LLM requires livekit-plugins-anthropic. "
                "Install: pip install livekit-plugins-anthropic"
            )
        logger.info(f"🧠 LLM: Anthropic Claude ({config.anthropic_model})")
        return anthropic_plugin.LLM(
            model=config.anthropic_model,
            api_key=config.anthropic_api_key or None,
        )

    # ─────────────────────────────────────
    # Groq (ultra-fast inference)
    # OpenAI-compatible API, free tier
    # Requires: GROQ_API_KEY
    # ─────────────────────────────────────
    elif provider == "groq":
        logger.info(f"🧠 LLM: Groq ({config.groq_model})")
        return openai_plugin.LLM(
            model=config.groq_model,
            api_key=config.groq_api_key or None,
            base_url="https://api.groq.com/openai/v1",
        )

    # ─────────────────────────────────────
    # DeepSeek
    # Excellent Bengali, very cheap, OpenAI-compatible
    # Requires: DEEPSEEK_API_KEY
    # ─────────────────────────────────────
    elif provider == "deepseek":
        logger.info(f"🧠 LLM: DeepSeek ({config.deepseek_model})")
        if not config.deepseek_api_key:
            raise ValueError(
                "DeepSeek requires DEEPSEEK_API_KEY in .env. "
                "Get one at https://platform.deepseek.com/"
            )
        return openai_plugin.LLM(
            model=config.deepseek_model,
            api_key=config.deepseek_api_key,
            base_url=config.deepseek_base_url,
        )

    # ─────────────────────────────────────
    # Custom OpenAI-compatible endpoint
    # Works with: Ollama, vLLM, LM Studio,
    # Together AI, Fireworks, OpenRouter, etc.
    #
    # Set in .env:
    #   CUSTOM_LLM_URL=http://localhost:11434/v1   (Ollama)
    #   CUSTOM_LLM_MODEL=llama3.1
    #   CUSTOM_LLM_API_KEY=not-needed
    # ─────────────────────────────────────
    elif provider == "custom":
        logger.info(
            f"🧠 LLM: Custom endpoint ({config.custom_llm_url}, "
            f"model={config.custom_llm_model})"
        )
        return openai_plugin.LLM(
            model=config.custom_llm_model,
            api_key=config.custom_llm_api_key,
            base_url=config.custom_llm_url,
        )

    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER: '{provider}'. "
            f"Valid options: gemini, openai, anthropic, groq, deepseek, custom"
        )
