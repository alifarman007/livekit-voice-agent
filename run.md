# Terminal 1: LiveKit Server
cd /c/Python_Projects/Voice_agent/livekit
./livekit-server.exe --dev

# Terminal 2: Agent Worker
cd /c/Python_Projects/Voice_agent/bangla-voice-agent
source .venv/Scripts/activate
python agent.py dev

# Terminal 3: Playground
cd /c/Python_Projects/Voice_agent/agents-playground
pnpm dev