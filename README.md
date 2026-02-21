# 🎙️ Bangla AI Voice Agent

A self-hosted, real-time Bengali (বাংলা) voice AI agent for call center operations in Bangladesh. Built on [LiveKit Agents](https://docs.livekit.io/agents/) framework, this agent handles customer calls with natural Bengali conversation — greeting callers with Islamic salam, collecting information, booking appointments, creating support tickets, and routing calls.

The agent persona is **Nusrat** (নুসরাত), a Bangladeshi receptionist who speaks natural Bengali, uses culturally appropriate greetings, and handles front-desk duties like a real human receptionist. She can switch between **6 different agent modes** — receptionist, sales, survey, collections, appointment, and support — with a single config change.

---

## 🎬 How It Works

```
Caller speaks Bengali
        │
        ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    STT       │────▶│     LLM      │────▶│     TTS      │
│  (5 options) │     │  (6 options) │     │  (7 options) │
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
- **6 agent modes** — receptionist, sales, survey, collections, appointment, support — switch via `.env`
- **11 function tools** — real integrations with Google Sheets CRM and Google Calendar
- **18 provider combinations** — 5 STT × 6 LLM × 7 TTS, all swappable via `.env`
- **Smart call flow** — automatic name/phone collection → customer lookup → registration → service
- **Silence detection** — 3-tier nudge system that speaks up like a human when the caller goes silent
- **Goodbye detection** — recognizes Bengali farewell phrases ("আচ্ছা রাখি", "রাখি তাহলে") and ends calls gracefully
- **Background audio** — office ambience and keyboard typing sounds for realism
- **Dynamic date awareness** — agent always knows today's date for accurate appointment scheduling
- **Custom LLM support** — plug in any OpenAI-compatible API (Ollama, vLLM, LM Studio, Together AI, etc.)

---

## 📁 Project Structure

```
livekit-voice-agent/
│
├── bangla-voice-agent/          # 🤖 Main agent code
│   ├── agent.py                 # Entry point — session setup, silence handling
│   ├── config.py                # Central config — reads .env, exposes typed settings
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example             # Template with all provider configs
│   ├── Dockerfile               # Container deployment
│   │
│   ├── prompts/                 # 🗣️ System prompts (agent personalities)
│   │   ├── __init__.py          # Prompt loader with dynamic date injection
│   │   ├── receptionist.py      # Front desk — routing, registration
│   │   ├── sales.py             # Outbound sales — lead qualification
│   │   ├── survey.py            # Customer satisfaction — NPS scoring
│   │   ├── collections.py       # Payment reminders — billing inquiries
│   │   ├── appointment.py       # Appointment-focused mode
│   │   └── support.py           # Support-focused mode
│   │
│   ├── providers/               # 🔌 Provider factories (STT/LLM/TTS)
│   │   ├── __init__.py          # Exports get_stt(), get_llm(), get_tts()
│   │   ├── stt_factory.py       # Google, Azure, Deepgram, ElevenLabs, AssemblyAI
│   │   ├── llm_factory.py       # Gemini, OpenAI, Anthropic, Groq, DeepSeek, Custom
│   │   └── tts_factory.py       # Google, Gemini, Azure, ElevenLabs, OpenAI, Cartesia
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

## 🤖 Agent Modes

Switch agent personality by changing `AGENT_MODE` in `.env`:

| Mode | Description | Use Case |
|------|-------------|----------|
| `receptionist` | Front desk — greeting, routing, registration | General inbound calls |
| `sales` | Outbound sales — lead qualification, product pitching | E-commerce, telecom |
| `survey` | Customer satisfaction — NPS scoring, feedback collection | Post-service feedback |
| `collections` | Payment reminders — billing inquiries, installment plans | Banks, ISPs, utilities |
| `appointment` | Focused on scheduling — slot checking, booking, cancellation | Clinics, salons, offices |
| `support` | Focused on tickets — troubleshooting, issue tracking | ISP, tech support |

```env
# Switch agent with one line:
AGENT_MODE=receptionist   # Default
AGENT_MODE=sales          # Outbound sales
AGENT_MODE=survey         # Customer feedback
AGENT_MODE=collections    # Payment reminders
```

All modes share the same Nusrat persona with Bengali conversation style, Islamic greetings, and the same 11 function tools.

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

## ⚙️ Provider Configuration

All providers are swappable via `.env` — no code changes needed.

### STT (Speech-to-Text) — 5 Options

| Provider | `.env` Value | Bengali Quality | Streaming | Cost |
|----------|-------------|-----------------|-----------|------|
| Google Cloud STT | `google` | ⭐⭐⭐⭐⭐ | ✅ | $0.024/min |
| Azure Speech | `azure` | ⭐⭐⭐⭐ | ✅ | $0.016/min |
| Deepgram Nova-3 | `deepgram` | ⭐⭐ | ✅ | $0.015/min |
| ElevenLabs Scribe | `elevenlabs` | ⭐⭐⭐ | ✅ | Free tier |
| AssemblyAI | `assemblyai` | ⭐⭐⭐ | ✅ | $0.015/min |

### LLM (Language Model) — 6 Options

| Provider | `.env` Value | Bengali Quality | Tool Calling | Cost |
|----------|-------------|-----------------|-------------|------|
| Google Gemini | `gemini` | ⭐⭐⭐⭐⭐ | ✅ | Cheapest |
| OpenAI GPT | `openai` | ⭐⭐⭐⭐ | ✅ | $0.15/1M input |
| Anthropic Claude | `anthropic` | ⭐⭐⭐⭐ | ✅ | $3/1M input |
| Groq | `groq` | ⭐⭐⭐ | ✅ | Free tier |
| DeepSeek | `deepseek` | ⭐⭐⭐⭐ | ✅ | Very cheap |
| Custom (OpenAI-compatible) | `custom` | Varies | Varies | Self-hosted |

The `custom` provider works with **any OpenAI-compatible API**: Ollama, vLLM, LM Studio, Together AI, Fireworks, OpenRouter, and self-hosted models like Llama 3.1, Qwen 3, Mistral, etc.

### TTS (Text-to-Speech) — 7 Options

| Provider | `.env` Value | Bengali Voice Quality | Streaming | Cost |
|----------|-------------|----------------------|-----------|------|
| Google Chirp3-HD | `google` | ⭐⭐⭐⭐ | ✅ | $4/1M chars |
| Gemini TTS | `gemini` | ⭐⭐⭐ | ✅ | Cheap |
| Azure Neural | `azure` | ⭐⭐⭐⭐ | ✅ | $16/1M chars |
| ElevenLabs | `elevenlabs` | ⭐⭐⭐⭐⭐ | ✅ | $120/1M chars |
| OpenAI TTS | `openai` | ⭐⭐ | ✅ | $15/1M chars |
| Cartesia Sonic-3 | `cartesia` | ⭐⭐ | ✅ | Varies |
| Custom | `custom` | Varies | Varies | Self-hosted |

**Recommended stack for Bengali:** Google STT + Gemini LLM + Google Chirp3-HD TTS (best accuracy, lowest cost).

```env
# Example: Switch to Azure STT + DeepSeek LLM + Azure TTS
STT_PROVIDER=azure
LLM_PROVIDER=deepseek
TTS_PROVIDER=azure

AZURE_SPEECH_KEY=your-key
AZURE_SPEECH_REGION=southeastasia
AZURE_TTS_VOICE=bn-BD-NabanitaNeural
DEEPSEEK_API_KEY=your-key
```

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

**Optional providers (install as needed):**
```bash
pip install livekit-plugins-azure        # Azure STT + TTS
pip install livekit-plugins-assemblyai   # AssemblyAI STT
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

See `.env.example` for all available configuration options.

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
| Crowd | `crowd` | Busy room |
| Typing | `typing` / `typing2` | Keyboard sounds (thinking indicator) |
| Hold Music | `hold_music` | Music while on hold |

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

**29 tests, 11 tools, 6 agent modes, 0 crashes.**

---

## 🗺️ Roadmap

- [x] Core voice agent with Bengali STT/TTS
- [x] Google Sheets CRM integration
- [x] Google Calendar appointment booking
- [x] Silence detection & nudge system
- [x] Background audio (office ambience + thinking sounds)
- [x] Goodbye detection & auto end-call
- [x] Dynamic date awareness
- [x] 6 agent modes (receptionist, sales, survey, collections, appointment, support)
- [x] 5 STT providers (Google, Azure, Deepgram, ElevenLabs, AssemblyAI)
- [x] 6 LLM providers (Gemini, OpenAI, Anthropic, Groq, DeepSeek, Custom)
- [x] 7 TTS providers (Google, Gemini, Azure, ElevenLabs, OpenAI, Cartesia, Custom)
- [x] Custom OpenAI-compatible LLM endpoint support
- [x] Comprehensive testing (11 rounds, 29 tests)
- [ ] VPS deployment
- [ ] SIP trunk integration (Bangladesh phone numbers)
- [ ] Production frontend
- [ ] Local TTS model (fine-tuned Bangladeshi Bangla)

---

## 💰 Cost Analysis

| Component | Provider | Cost |
|-----------|----------|------|
| STT | Google Cloud | ~$0.024/min |
| STT | Azure Speech | ~$0.016/min |
| LLM | Gemini Flash | ~$0.01/1K tokens |
| LLM | DeepSeek | ~$0.001/1K tokens |
| TTS | Google Chirp3-HD | ~$4/1M characters |
| TTS | Azure Neural | ~$16/1M characters |
| TTS | ElevenLabs | ~$120/1M characters |

Google Cloud stack (STT + Gemini + TTS) is approximately **$0.03-0.05 per minute of conversation** — the most cost-effective option for Bengali.

---

## 🤝 Contributing

This project is in active development. Contributions are welcome for:
- Additional language support
- New tool integrations
- SIP trunk providers for Bangladesh
- Local TTS/STT model optimization
- New agent mode prompts

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
