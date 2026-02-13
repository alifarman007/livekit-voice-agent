# 🎙️ Bangla Voice Agent

A modular, production-ready AI voice calling agent built on **LiveKit Agents**. Everything is swappable via `.env` — STT, LLM, TTS, telephony, language, and agent personality.

**Like Vapi, but you own it.**

## Features

- 🇧🇩 **Native Bangla support** — STT, LLM, and TTS all optimized for Bengali
- 🔌 **Plug-and-play providers** — Swap STT/LLM/TTS by changing one line in `.env`
- 📞 **Appointment booking** — Full scheduling with availability checking
- 🗂️ **CRM integration** — Customer lookup, notes, support tickets
- 📱 **Call transfer** — Route to departments, escalate to humans
- 🎭 **Multiple modes** — Receptionist, appointment booker, support assistant
- 🐳 **Docker ready** — One command to deploy to production
- 💰 **Free to test** — Uses Google Cloud free tier

## Supported Providers

| Layer | Providers |
|-------|-----------|
| **STT** | Google Cloud, ElevenLabs, Deepgram, Custom (your Whisper model) |
| **LLM** | Gemini, OpenAI, Claude, Groq, Custom (any OpenAI-compatible) |
| **TTS** | Google Cloud, Gemini TTS, ElevenLabs, OpenAI, Cartesia, Custom (your VITS) |
| **Telephony** | Twilio, Telnyx, SignalWire, Custom SIP (add later) |

## Quick Start

### Prerequisites

- Python 3.10–3.13
- Google API key (free: [aistudio.google.com/apikey](https://aistudio.google.com/apikey))
- Google Cloud project with Speech-to-Text & Text-to-Speech APIs enabled

### 1. Clone & Install

```bash
cd bangla-voice-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Download VAD & turn detection models
python -c "from livekit.plugins import silero; silero.VAD.load()"
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your API keys
```

Minimum required: `GOOGLE_API_KEY` for Gemini LLM.
For STT/TTS: either `GOOGLE_APPLICATION_CREDENTIALS` or `gcloud auth application-default login`.

### 3. Run

#### Option A: Console Mode (Terminal mic/speaker — simplest)
```bash
python agent.py console
```
Talk directly through your microphone. No server needed.

#### Option B: Dev Mode (Browser — production-like)
```bash
# Terminal 1: Start local LiveKit server
# Install: https://docs.livekit.io/transport/self-hosting/local/
livekit-server --dev

# Terminal 2: Start the agent
python agent.py dev

# Open browser: Go to LiveKit Playground
# https://agents-playground.livekit.io
# Connect with: ws://localhost:7880, API key: devkey, Secret: secret
```

## Configuration Guide

### Swap STT Provider
```env
# In .env:
STT_PROVIDER=deepgram       # Change from 'google' to 'deepgram'
DEEPGRAM_API_KEY=your-key   # Add the API key
```

### Swap LLM Provider
```env
LLM_PROVIDER=openai          # Change from 'gemini' to 'openai'
OPENAI_API_KEY=sk-xxx        # Add the API key
OPENAI_MODEL=gpt-4o-mini     # Optionally change model
```

### Swap TTS Provider
```env
TTS_PROVIDER=elevenlabs      # Change from 'google' to 'elevenlabs'
ELEVEN_API_KEY=your-key      # Add the API key
ELEVEN_VOICE_ID=voice-id     # Choose a voice
```

### Change Agent Mode
```env
AGENT_MODE=appointment    # receptionist | appointment | support
```

### Change Language
```env
LANGUAGE=en-US    # bn-BD (Bangla) | en-US | hi-IN | etc.
```

## Project Structure

```
bangla-voice-agent/
├── agent.py              # Main entry point
├── config.py             # Central configuration reader
├── providers/
│   ├── stt_factory.py    # STT provider selector
│   ├── llm_factory.py    # LLM provider selector
│   └── tts_factory.py    # TTS provider selector
├── tools/
│   ├── appointment.py    # Appointment booking functions
│   ├── crm.py            # CRM lookup & update functions
│   └── transfer.py       # Call transfer & escalation
├── prompts/
│   ├── receptionist.py   # Receptionist personality (Bangla)
│   ├── appointment.py    # Appointment booker personality
│   └── support.py        # Support assistant personality
├── .env.example          # All configuration options
├── requirements.txt      # Python dependencies
├── Dockerfile            # Production deployment
└── README.md
```

## Adding Your Custom Models Later

### Custom Bangla STT (your fine-tuned Whisper)
1. Run your model as a FastAPI server on port 8001
2. Set in `.env`:
   ```env
   STT_PROVIDER=custom
   CUSTOM_STT_URL=http://localhost:8001/stt
   ```
3. Implement the custom STT class in `providers/stt_factory.py`

### Custom Bangla TTS (your VITS model)
1. Run your VITS model as a FastAPI server on port 8002
2. Set in `.env`:
   ```env
   TTS_PROVIDER=custom
   CUSTOM_TTS_URL=http://localhost:8002/tts
   ```
3. Implement the custom TTS class in `providers/tts_factory.py`

### Adding Telephony (phone calls)
1. Get a SIP trunk from Twilio/Telnyx
2. Set up LiveKit SIP integration
3. No code changes needed — just config

## Production Deployment

```bash
# Build Docker image
docker build -t bangla-voice-agent .

# Run with production config
docker run -d \
  --env-file .env \
  --name voice-agent \
  bangla-voice-agent
```

## Cost Comparison

| Scale | Vapi | This Agent (API) | Savings |
|-------|------|-------------------|---------|
| 1,000 min/mo | $130-310 | $30-50 | **77-84%** |
| 10,000 min/mo | $1,300-3,100 | $300-500 | **77-84%** |
| 100,000 min/mo | $13,000-31,000 | $3,000-5,000 | **77-84%** |

## License

MIT
