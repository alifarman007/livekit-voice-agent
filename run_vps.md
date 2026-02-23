# VPS Run Guide — Start All Services

> **VPS:** Contabo Cloud VPS 10 (161.97.98.67)
> **OS:** Ubuntu 24.04
> **Domain:** https://landphoneai.duckdns.org
> **SSH:** `ssh root@161.97.98.67`

---

## Quick Start (4 SSH Terminals)

Open 4 separate SSH sessions to the VPS:

```bash
ssh root@161.97.98.67
```

### Terminal 1: LiveKit Server
```bash
cd /root/projects/livekit-voice-agent/livekit
./livekit-server --config livekit-config.yaml
```
Wait for: `starting LiveKit server`

### Terminal 2: Voice Agent
```bash
cd /root/projects/livekit-voice-agent/bangla-voice-agent
source .venv/bin/activate
python3.11 agent.py dev
```
Wait for: `registered worker`

### Terminal 3: Playground (Web UI)
```bash
cd /root/projects/livekit-voice-agent/agents-playground
pnpm start -H 0.0.0.0
```
Access at: **https://landphoneai.duckdns.org**

### Terminal 4: SIP Service (Phone Calls)
```bash
docker rm -f livekit-sip 2>/dev/null
docker run -d --name livekit-sip \
  --network host \
  -v /root/projects/livekit-voice-agent/livekit/sip-config.yaml:/etc/sip.yaml \
  livekit/sip \
  --config /etc/sip.yaml
```
Verify: `docker logs livekit-sip`

---

## Verify Everything Is Running

```bash
# Redis
redis-cli ping
# Expected: PONG

# LiveKit Server (port 7880)
ss -tlnp | grep 7880

# Agent
# Terminal 2 should show "registered worker"

# Playground (port 3000)
curl -I http://localhost:3000

# SIP (port 5060)
docker ps | grep livekit-sip
ss -ulnp | grep 5060
```

---

## Stop Services

```bash
# Terminal 1, 2, 3: Ctrl+C

# SIP container:
docker stop livekit-sip
```

---

## Test

- **Web:** Open https://landphoneai.duckdns.org → Click Connect → Talk
- **Phone:** Call +1 774 500 7904 from a verified number

---

## Change Agent Mode

Edit `/root/projects/livekit-voice-agent/bangla-voice-agent/.env`:
```env
AGENT_MODE=receptionist
# Options: receptionist, sales, survey, collections, appointment, support
```
Then restart Terminal 2 (Ctrl+C → rerun command).

---

## Notes

- If terminals close, all services stop. Use `screen` or `tmux` to keep them running in background.
- Agent connects locally: `LIVEKIT_URL=ws://localhost:7880`
- Browser connects via domain: `NEXT_PUBLIC_LIVEKIT_URL=wss://landphoneai.duckdns.org`
- SIP runs as Docker container with `--network host` (shares VPS network)
- Redis must be running before LiveKit Server and SIP start
