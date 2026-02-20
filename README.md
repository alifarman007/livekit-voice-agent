# 🎙️ Bangla AI Voice Agent

A self-hosted, real-time Bengali (বাংলা) voice AI agent for call center operations in Bangladesh. Built on [LiveKit Agents](https://docs.livekit.io/agents/) framework, this agent handles customer calls with natural Bengali conversation — greeting callers with Islamic salam, collecting information, booking appointments, creating support tickets, and routing calls.

The agent persona is **Nusrat** (নুসরাত), a Bangladeshi receptionist who speaks natural Bengali, uses culturally appropriate greetings, and handles front-desk duties like a real human receptionist.

---

## 🎬 How It Works

```
Caller speaks Bengali
        │
        ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Google STT  │────▶│  Gemini LLM  │────▶│  Google TTS  │
│  (bn-BD)     │     │  (3.0 Flash) │     │  (Chirp3-HD) │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │                      │
                     Tool Calls                    │
                     ┌──────┴───────┐              │
                     │ Google Sheets│              ▼
                     │ Google Cal   │     Caller hears Bengali
                     │ Call Routing │
                     └──────────────┘
```

The agent uses LiveKit's room-based architecture for real-time bidirectional audio streaming. A browser-based playground serves as the test interface, with SIP trunk integration planned for production phone connectivity.

---

## ✨ Features

- **Natural Bengali conversation** — culturally appropriate Islamic greetings, colloquial filler words ("জি", "আচ্ছা", "বলুন"), and short phone-appropriate responses
- **11 function tools** — real integrations with Google Sheets CRM and Google Calendar
- **Smart call flow** — automatic name/phone collection → customer lookup → registration → service
- **Silence detection** — 3-tier nudge system that speaks up like a human when the caller goes silent
- **Goodbye detection** — recognizes Bengali farewell phrases ("আচ্ছা রাখি", "রাখি তাহলে") and ends calls gracefully
- **Background audio** — office ambience and keyboard typing sounds for realism
- **Swappable providers** — change STT/LLM/TTS providers via `.env` without touching code
- **Dynamic date awareness** — agent always knows today's date for accurate appointment scheduling

---

## 📁 Project Structure

```
livekit-voice-agent/
│
├── bangla-voice-agent/          # 🤖 Main agent code
│   ├── agent.py                 # Entry point — session setup, silence handling
│   ├── config.py                # Central config — reads .env, exposes typed settings
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile               # Container deployment
│   │
│   ├── prompts/                 # 🗣️ System prompts (agent personality)
│   │   ├── __init__.py          # Prompt loader with dynamic date injection
│   │   ├── receptionist.py      # Main receptionist persona (Nusrat)
│   │   ├── appointment.py       # Appointment-focused mode
│   │   └── support.py           # Support-focused mode
│   │
│   ├── providers/               # 🔌 Provider factories (STT/LLM/TTS)
│   │   ├── __init__.py          # Exports get_stt(), get_llm(), get_tts()
│   │   ├── stt_factory.py       # Google, Deepgram, ElevenLabs STT
│   │   ├── llm_factory.py       # Gemini, OpenAI, Anthropic, Groq LLM
│   │   └── tts_factory.py       # Google Chirp3-HD, ElevenLabs, Cartesia TTS
│   │
│   └── tools/                   # 🛠️ Function tools (LLM calls these)
│       ├── __init__.py
│       ├── crm.py               # Google Sheets CRM integration
│       ├── appointment.py       # Google Calendar booking
│       └── transfer.py          # Call routing & end call
│
├── agents-playground/           # 🖥️ LiveKit Agents Playground (Next.js)
│   ├── src/                     # Frontend source code
│   ├── package.json
│   └── ...
│
├── livekit/                     # 📡 LiveKit server binary
│   └── LICENSE
│
└── run.md                       # Quick-start run commands
```

---

## 🛠️ Function Tools

The agent has 11 tools that perform real actions:

| Tool | What It Does | Integration |
|------|-------------|-------------|
| `register_customer` | Register new customer with name + phone | Google Sheets |
| `lookup_customer` | Find existing customer by phone number | Google Sheets |
| `update_customer_notes` | Append notes to customer record (preserves existing) | Google Sheets |
| `create_support_ticket` | Create prioritized support ticket with ID | Google Sheets |
| `check_available_slots` | Show available appointment times for a date | Google Calendar |
| `book_appointment` | Book a calendar appointment | Google Calendar |
| `cancel_appointment` | Cancel existing appointment by name + date | Google Calendar |
| `get_next_available` | Find the next open slot | Google Calendar |
| `transfer_to_department` | Route call to sales/support/billing | Logging (SIP in production) |
| `escalate_to_human` | Escalate to human agent | Logging (SIP in production) |
| `end_call` | End call with summary | Session control |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** with virtual environment
- **Node.js 18+** with pnpm
- **Google Cloud** service account with:
  - Speech-to-Text API enabled
  - Text-to-Speech API enabled
  - Generative Language API (Gemini) enabled
  - Google Sheets API enabled
  - Google Calendar API enabled
- **LiveKit Server** binary ([download](https://github.com/livekit/livekit/releases))

### 1. Clone the Repository

```bash
git clone https://github.com/alifarman007/livekit-voice-agent.git
cd livekit-voice-agent
```

### 2. Setup Python Environment

```bash
cd bangla-voice-agent
python -m venv .venv

# Windows (MINGW64/Git Bash)
source .venv/Scripts/activate

# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure Environment

Create `bangla-voice-agent/.env`:

```env
# ══════════════════════════════════════
# Provider Selection (swap without code changes)
# ══════════════════════════════════════
STT_PROVIDER=google
LLM_PROVIDER=gemini
TTS_PROVIDER=google

# ══════════════════════════════════════
# Language & Mode
# ══════════════════════════════════════
LANGUAGE=bn-BD
AGENT_MODE=receptionist

# ══════════════════════════════════════
# Google Cloud Credentials
# ══════════════════════════════════════
GOOGLE_APPLICATION_CREDENTIALS=gcloud-key.json
GOOGLE_API_KEY=your-gemini-api-key

# ══════════════════════════════════════
# Google Sheets CRM
# ══════════════════════════════════════
GOOGLE_SHEET_ID=your-google-sheet-id

# ══════════════════════════════════════
# Google Calendar
# ══════════════════════════════════════
GOOGLE_CALENDAR_ID=your-calendar-id@group.calendar.google.com

# ══════════════════════════════════════
# Google Cloud TTS Voice
# ══════════════════════════════════════
GOOGLE_TTS_VOICE=bn-IN-Chirp3-HD-Kore
GOOGLE_TTS_SPEAKING_RATE=1.0
GOOGLE_TTS_PITCH=0.0

# ══════════════════════════════════════
# LiveKit Server
# ══════════════════════════════════════
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret

# ══════════════════════════════════════
# Background Audio
# ══════════════════════════════════════
BACKGROUND_AUDIO_ENABLED=true
BACKGROUND_AUDIO_TYPE=office
BACKGROUND_AUDIO_VOLUME=0.8
THINKING_SOUND_ENABLED=true
THINKING_SOUND_TYPE=typing2
THINKING_SOUND_VOLUME=0.1
```

### 4. Setup Google Sheets CRM

Create a Google Sheet with these headers in Row 1:

| A | B | C | D | E | F | G |
|---|---|---|---|---|---|---|
| Name | Phone | Email | Company | Last Interaction | Notes | Status |

Share the sheet with your service account email (found in `gcloud-key.json` → `client_email`).

### 5. Setup Google Calendar

Create a new Google Calendar. Share it with your service account email (Editor access). Copy the Calendar ID from Settings → Integrate calendar.

### 6. Setup Playground Frontend

```bash
cd agents-playground
pnpm install
```

Create `agents-playground/.env.local`:

```env
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
NEXT_PUBLIC_LIVEKIT_URL=ws://localhost:7880
```

### 7. Run Everything

Open **3 terminals** and run simultaneously:

**Terminal 1 — LiveKit Server:**
```bash
cd livekit
./livekit-server --dev
```

**Terminal 2 — Voice Agent:**
```bash
cd bangla-voice-agent
source .venv/Scripts/activate   # Windows
python agent.py dev
```

**Terminal 3 — Playground Frontend:**
```bash
cd agents-playground
pnpm dev
```

Open **http://localhost:3000** in your browser, click Connect, and start talking in Bengali.

---

## 🗣️ Conversation Flow

A typical call follows this pattern:

```
Nusrat: "আসসালামু আলাইকুম, আমাদের কোম্পানি-এ স্বাগতম।
         আমি নুসরাত। আপনার নামটা জানতে পারি?"

Caller: "আমার নাম করিম"

Nusrat: "জি করিম ভাই, আপনার মোবাইল নম্বরটা বলুন।"

Caller: "০১৬৫৩২৯"

Nusrat: "একটু দেখছি...
         করিম ভাই, আপনাকে চিনতে পেরেছি। কিভাবে সাহায্য করতে পারি?"

Caller: "আমার ইন্টারনেট কাজ করছে না"

Nusrat: "দুঃখিত শুনে। আচ্ছা, টিকিট করে দিচ্ছি একটু অপেক্ষা করুন...
         করিম ভাই, হাই প্রায়োরিটি সাপোর্ট টিকিট তৈরি করে দিয়েছি।
         আর কিছু কি সাহায্য লাগবে?"

Caller: "আচ্ছা রাখি তাহলে"

Nusrat: "আচ্ছা রাখি তাহলে। আর কিছু লাগলে কল দিবেন।
         আসসালামু আলাইকুম।"
         [end_call tool fires]
```

---

## ⚙️ Provider Configuration

Swap any component by changing one line in `.env`:

### STT (Speech-to-Text)
| Provider | `.env` Value | Language Support |
|----------|-------------|-----------------|
| Google Cloud STT | `STT_PROVIDER=google` | bn-BD (Bengali) ✅ |
| Deepgram | `STT_PROVIDER=deepgram` | Limited Bengali |
| ElevenLabs | `STT_PROVIDER=elevenlabs` | Multilingual |

### LLM (Language Model)
| Provider | `.env` Value | Model |
|----------|-------------|-------|
| Google Gemini | `LLM_PROVIDER=gemini` | gemini-2.5-flash |
| OpenAI | `LLM_PROVIDER=openai` | gpt-4o-mini |
| Anthropic | `LLM_PROVIDER=anthropic` | claude-sonnet-4-5 |
| Groq | `LLM_PROVIDER=groq` | qwen-qwq-32b |

### TTS (Text-to-Speech)
| Provider | `.env` Value | Voice |
|----------|-------------|-------|
| Google Chirp3-HD | `TTS_PROVIDER=google` | bn-IN-Chirp3-HD-Kore ✅ |
| ElevenLabs | `TTS_PROVIDER=elevenlabs` | Multilingual v2 |
| Cartesia | `TTS_PROVIDER=cartesia` | Custom voices |

The recommended stack for Bengali is **Google STT + Gemini LLM + Google Chirp3-HD TTS** for best language accuracy and cost efficiency.

---

## 🔇 Silence Handling

The agent detects when callers go silent and responds like a human would:

| Silence Duration | Agent Response |
|-----------------|---------------|
| ~10 seconds | "হ্যালো? বলুন, আমি শুনছি।" |
| ~20 seconds | "আপনি কি শুনতে পাচ্ছেন? আমি আপনার কথা শুনতে পাচ্ছি না।" |
| ~30 seconds | "ঠিক আছে, মনে হচ্ছে লাইনে সমস্যা হচ্ছে। আসসালামু আলাইকুম।" → `end_call` |

The counter resets whenever the caller speaks again.

---

## 🔊 Background Audio

Built-in ambient sounds make calls feel like a real office:

| Sound | Config Value | Description |
|-------|-------------|-------------|
| Office | `office` | General office ambience |
| City | `city` | Urban background |
| Crowd | `crowded` | Busy room |
| Typing | `typing` / `typing2` | Keyboard sounds (thinking indicator) |
| Hold Music | `hold_music` | Music while on hold |

Configured via `.env`:
```env
BACKGROUND_AUDIO_ENABLED=true
BACKGROUND_AUDIO_TYPE=office
BACKGROUND_AUDIO_VOLUME=0.8
THINKING_SOUND_ENABLED=true
THINKING_SOUND_TYPE=typing2
THINKING_SOUND_VOLUME=0.1
```

---

## 🧪 Test Results

All 11 rounds of comprehensive testing passed:

| Round | Tests | Status |
|-------|-------|--------|
| Connection & Greeting | 2 | ✅ Passed |
| Customer Lookup & Registration | 3 | ✅ Passed |
| Appointment Booking Flow | 3 | ✅ Passed |
| Support Ticket + Notes | 2 | ✅ Passed |
| Routing & Escalation | 3 | ✅ Passed |
| Silence & Nudge System | 1 | ✅ Passed |
| Background Audio | 1 | ✅ Passed |
| Bengali Language Quality | 1 | ✅ Passed |
| Edge Cases & Error Handling | 1 | ✅ Passed |
| End-to-End Customer Journey | 9 | ✅ Passed |
| Stress & Stability | 3 | ✅ Passed |

**29 tests, 11 tools, 0 crashes.**

---

## 🗺️ Roadmap

- [x] Core voice agent with Bengali STT/TTS
- [x] Google Sheets CRM integration
- [x] Google Calendar appointment booking
- [x] Silence detection & nudge system
- [x] Background audio (office ambience + thinking sounds)
- [x] Goodbye detection & auto end-call
- [x] Dynamic date awareness
- [x] Comprehensive testing (11 rounds)
- [ ] VPS deployment
- [ ] SIP trunk integration (Bangladesh phone numbers)
- [ ] Production frontend
- [ ] Local TTS model (fine-tuned Bangladeshi Bangla)

---

## 💰 Cost Analysis

| Component | Provider | Cost |
|-----------|----------|------|
| STT | Google Cloud | ~$0.024/min |
| LLM | Gemini Flash | ~$0.01/1K tokens |
| TTS | Google Chirp3-HD | ~$4/1M characters |
| TTS (alternative) | ElevenLabs | ~$120/1M characters |

Google Cloud TTS is approximately **40x cheaper** than ElevenLabs while providing good Bengali voice quality through the Chirp3-HD model.

---

## 🤝 Contributing

This project is in active development. Contributions are welcome for:
- Additional language support
- New tool integrations
- SIP trunk providers for Bangladesh
- Local TTS model optimization

---

## 📜 License

MIT License — see [LICENSE](bangla-voice-agent/LICENSE) for details.

---

## 🙏 Acknowledgments

- [LiveKit](https://livekit.io/) — Real-time communication framework
- [Google Cloud](https://cloud.google.com/) — STT, TTS, Gemini, Sheets, Calendar APIs
- [Silero VAD](https://github.com/snakers4/silero-vad) — Voice Activity Detection

---

**Built for Bangladesh 🇧🇩 — by [Alif Arman](https://github.com/alifarman007)**
