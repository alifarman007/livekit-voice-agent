# SIP Trunk Setup Guide — Connect Real Phone Calls to LiveKit Voice Agent

> **Purpose:** This guide enables anyone to connect a real phone number to a LiveKit voice agent so that callers can talk to the AI agent over a regular phone call. No coding knowledge required — just follow the steps.
>
> **Tested with:** LiveKit Server 1.9.11, LiveKit SIP (Docker), Twilio Elastic SIP Trunking, Ubuntu 24.04

---

## Table of Contents

1. [Overview — How It Works](#1-overview--how-it-works)
2. [Prerequisites](#2-prerequisites)
3. [Step 1: Install Redis](#step-1-install-redis)
4. [Step 2: Configure LiveKit Server with Redis](#step-2-configure-livekit-server-with-redis)
5. [Step 3: Install LiveKit CLI](#step-3-install-livekit-cli)
6. [Step 4: Install LiveKit SIP (Docker)](#step-4-install-livekit-sip-docker)
7. [Step 5: Set Up Twilio Account & Phone Number](#step-5-set-up-twilio-account--phone-number)
8. [Step 6: Create Twilio Elastic SIP Trunk](#step-6-create-twilio-elastic-sip-trunk)
9. [Step 7: Create LiveKit SIP Inbound Trunk](#step-7-create-livekit-sip-inbound-trunk)
10. [Step 8: Create LiveKit SIP Dispatch Rule](#step-8-create-livekit-sip-dispatch-rule)
11. [Step 9: Open Firewall Ports](#step-9-open-firewall-ports)
12. [Step 10: Start All Services](#step-10-start-all-services)
13. [Step 11: Test the Phone Call](#step-11-test-the-phone-call)
14. [Complete Service Startup Checklist](#complete-service-startup-checklist)
15. [Troubleshooting](#troubleshooting)
16. [Reference — All Config Files](#reference--all-config-files)
17. [Reference — All Commands Cheat Sheet](#reference--all-commands-cheat-sheet)
18. [Changing Phone Numbers or VPS](#changing-phone-numbers-or-vps)

---

## 1. Overview — How It Works

```
Caller's Phone
     │
     ▼
Twilio Phone Number (+1-XXX-XXX-XXXX)
     │
     ▼ (SIP Protocol)
Twilio Elastic SIP Trunk
     │
     ▼ (SIP over UDP, port 5060)
Your VPS → LiveKit SIP Service (Docker container)
     │
     ▼ (Internal, via Redis)
LiveKit Server
     │
     ▼ (Creates a room, agent joins)
Your Voice Agent (Python)
     │
     ▼ (Agent speaks back)
Caller hears AI voice
```

**Key Components:**
- **Twilio** — Provides the phone number and routes calls via SIP
- **LiveKit SIP** — Receives SIP calls and bridges them into LiveKit rooms
- **LiveKit Server** — Manages rooms and connects agents to callers
- **Redis** — Required for LiveKit Server and SIP to communicate
- **Voice Agent** — Your Python agent that handles the conversation

---

## 2. Prerequisites

Before starting, ensure you have:

- [ ] A VPS with Ubuntu (20.04, 22.04, or 24.04) with root/sudo access
- [ ] A public IPv4 address for your VPS
- [ ] LiveKit Server binary installed on the VPS
- [ ] Your voice agent code deployed and working via the web playground
- [ ] Python environment set up with all agent dependencies
- [ ] A credit/debit card for Twilio signup (free trial gives $15 credit)

**Ports that must be open:**

| Port | Protocol | Purpose |
|------|----------|---------|
| 5060 | UDP + TCP | SIP signaling (Twilio → your VPS) |
| 7880 | TCP | LiveKit API |
| 7881 | TCP | LiveKit RTC |
| 50000-60000 | UDP | WebRTC media (voice data) |

---

## Step 1: Install Redis

LiveKit Server and LiveKit SIP communicate through Redis. Without Redis, SIP will not work.

```bash
# Install Redis
apt update
apt install -y redis-server

# Enable Redis to start on boot
systemctl enable redis-server

# Start Redis
systemctl start redis-server

# Verify Redis is running
redis-cli ping
```

**Expected output:** `PONG`

**If Redis fails to start:**
```bash
# Check status
systemctl status redis-server

# Check logs
journalctl -u redis-server --no-pager -n 20

# Try restarting
systemctl restart redis-server
```

---

## Step 2: Configure LiveKit Server with Redis

LiveKit Server must be configured to use Redis (instead of `--dev` mode) for SIP to work.

**Create the config file:**

```bash
cat > /root/projects/livekit-voice-agent/livekit/livekit-config.yaml << 'EOF'
port: 7880
bind_addresses:
  - 0.0.0.0
rtc:
  tcp_port: 7881
  port_range_start: 50000
  port_range_end: 60000
  use_external_ip: true
redis:
  address: localhost:6379
keys:
  devkey: secret
EOF
```

> **⚠️ IMPORTANT:** Replace `devkey` and `secret` with your actual API key and secret.
> The key `devkey` with secret `secret` matches the default `--dev` mode credentials.
> For production, use a secret that is at least 32 characters long.

> **📌 NOTE:** The `keys` section format is `api_key: api_secret`. The agent's `.env` file must have matching `LIVEKIT_API_KEY` and `LIVEKIT_API_SECRET` values.

**Start LiveKit Server with this config:**
```bash
cd /root/projects/livekit-voice-agent/livekit
./livekit-server --config livekit-config.yaml
```

**Expected output (key lines):**
```
INFO  livekit  redis/redis.go  connecting to redis  {"addr": "localhost:6379"}
INFO  livekit  service/server.go  starting LiveKit server  {"portHttp": 7880, ...}
```

> **⚠️ Warning about short secret:** You may see `ERROR: secret is too short, should be at least 32 characters`. This is a warning only — the server still starts. Fix it by using a longer secret in production.

---

## Step 3: Install LiveKit CLI

The CLI is used to create SIP trunks and dispatch rules.

```bash
curl -sSL https://get.livekit.io/cli | bash
```

**If the install script fails**, you can download manually from:
https://github.com/livekit/livekit-cli/releases

Download the `lk_X.X.X_linux_amd64.tar.gz` file, upload to VPS, extract:
```bash
tar -xzf lk_X.X.X_linux_amd64.tar.gz
mv lk /usr/local/bin/
```

**Configure the CLI to connect to your LiveKit Server:**
```bash
lk project add local --url http://127.0.0.1:7880 --api-key devkey --api-secret secret --default
```

> **📌 NOTE:** Replace `devkey` and `secret` with your actual credentials matching the LiveKit config.

**Verify it works:**
```bash
lk room list --url http://127.0.0.1:7880
```

**Expected output:** An empty table (no rooms yet) — no errors.

---

## Step 4: Install LiveKit SIP (Docker)

LiveKit SIP is the bridge between phone calls (SIP protocol) and LiveKit rooms.

**Install Docker (if not already installed):**
```bash
apt install -y docker.io
systemctl enable docker
systemctl start docker
```

**Pull the LiveKit SIP Docker image:**
```bash
docker pull livekit/sip
```

**Create the SIP configuration file:**
```bash
cat > /root/projects/livekit-voice-agent/livekit/sip-config.yaml << 'EOF'
api_key: devkey
api_secret: secret
ws_url: ws://localhost:7880
redis:
  address: localhost:6379
sip:
  port: 5060
logging:
  level: info
EOF
```

> **📌 NOTE:** `api_key`, `api_secret` must match your LiveKit Server config.
> `ws_url` should be `ws://localhost:7880` (SIP runs on the same machine as LiveKit).

**Do NOT start the SIP container yet** — we need to set up Twilio first.

---

## Step 5: Set Up Twilio Account & Phone Number

### 5a. Create Twilio Account

1. Go to **https://www.twilio.com/try-twilio**
2. Sign up with email (free trial gives **$15 credit**)
3. Verify your email and phone number during signup

### 5b. Buy a Phone Number

1. In Twilio Console → **Phone Numbers** → **Manage** → **Buy a Number**
2. Search for a number with **Voice** capability
3. Buy the number (costs ~$1.15/month from your trial credit)
4. Note down the number (e.g., `+17745007904`)

### 5c. Verify Your Caller ID (REQUIRED for Trial Accounts)

> **⚠️ CRITICAL:** Twilio trial accounts can ONLY receive calls from **verified phone numbers**. If you skip this step, calls will fail with error `21264 - 'From' phone number not verified`.

1. Go to **Phone Numbers** → **Manage** → **Verified Caller IDs**
2. Click **Add a new Caller ID**
3. Enter the phone number you will be calling FROM (e.g., your personal mobile number)
4. Choose verification method (call or SMS)
5. Enter the verification code
6. Repeat for any other numbers that will call the agent

---

## Step 6: Create Twilio Elastic SIP Trunk

This tells Twilio to forward phone calls to your VPS via SIP protocol.

### 6a. Create the Trunk

1. In Twilio Console → **Explore Products** → **Elastic SIP Trunking** (under Super Network section)
2. Click **Trunks** → **Create new trunk**
3. Name: `LiveKit-Agent` (or any name you prefer)
4. Click **Create**

### 6b. Configure Origination

This tells Twilio WHERE to send calls (your VPS).

1. Click on your new trunk → **Origination** tab
2. Click **Add new Origination URI**
3. Enter: `sip:YOUR_VPS_IP:5060;transport=udp`
   - Example: `sip:161.97.98.67:5060;transport=udp`
4. Priority: `10`, Weight: `10`
5. Click **Add**

### 6c. Associate Your Phone Number

1. Click on your trunk → **Numbers** tab
2. Click **Add a Number**
3. Select your phone number (e.g., `+17745007904`)
4. Click **Add Selected**

### 6d. Verify Number Routing

1. Go to **Phone Numbers** → **Manage** → **Active Numbers**
2. Click on your number
3. Under **Voice Configuration**, it should show **SIP Trunk** as the handler
4. If it still shows "Webhook", change it to your SIP Trunk

---

## Step 7: Create LiveKit SIP Inbound Trunk

This tells LiveKit SIP which phone numbers to expect incoming calls from.

```bash
lk sip inbound create \
  --name "Twilio Inbound" \
  --numbers "+17745007904" \
  --url http://127.0.0.1:7880
```

> **📌 Replace `+17745007904` with YOUR Twilio phone number (with country code and `+` prefix).**

**Expected output:**
```
SIPTrunkID: ST_xxxxxxxxxxxx
```

**Save this Trunk ID** — you may need it for troubleshooting.

**Verify it was created:**
```bash
lk sip inbound list --url http://127.0.0.1:7880
```

**To delete and recreate (if you made a mistake):**
```bash
lk sip inbound delete ST_xxxxxxxxxxxx --url http://127.0.0.1:7880
```

---

## Step 8: Create LiveKit SIP Dispatch Rule

This tells LiveKit what to do when a phone call arrives — create a room and connect the agent.

```bash
lk sip dispatch create \
  --name "Route to Agent" \
  --direct "phone-call" \
  --url http://127.0.0.1:7880
```

This creates a rule that puts all incoming SIP calls into a LiveKit room called `phone-call`. Your voice agent will automatically join this room and start talking to the caller.

**Expected output:**
```
SIPDispatchRuleID: SDR_xxxxxxxxxxxx
```

**Verify it was created:**
```bash
lk sip dispatch list --url http://127.0.0.1:7880
```

**Expected output:**
```
┌───────────────────┬────────────────┬───────────┬────────┬────────────┬─────┐
│ SipDispatchRuleID │ Name           │ SipTrunks │ Type   │ RoomName   │ Pin │
├───────────────────┼────────────────┼───────────┼────────┼────────────┼─────┤
│ SDR_xxxxx         │ Route to Agent │ <any>     │ Direct │ phone-call │     │
└───────────────────┴────────────────┴───────────┴────────┴────────────┴─────┘
```

---

## Step 9: Open Firewall Ports

Ensure all required ports are open:

```bash
# SIP signaling
ufw allow 5060/udp
ufw allow 5060/tcp

# LiveKit (if not already open)
ufw allow 7880/tcp
ufw allow 7881/tcp
ufw allow 50000:60000/udp

# Verify
ufw status
```

**Expected:** All ports listed as `ALLOW`.

> **📌 If using a cloud provider with an external firewall** (AWS Security Groups, GCP Firewall Rules, Contabo Firewall panel), you must ALSO allow these ports there. VPS-level `ufw` alone is not enough if the cloud provider has its own firewall.

---

## Step 10: Start All Services

You need **4 services running** in separate SSH terminals (or use systemd/screen/tmux):

### Terminal 1 — LiveKit Server
```bash
cd /root/projects/livekit-voice-agent/livekit
./livekit-server --config livekit-config.yaml
```

### Terminal 2 — Voice Agent
```bash
cd /root/projects/livekit-voice-agent/bangla-voice-agent
source .venv/bin/activate
python3.11 agent.py dev
```

Wait for: `registered worker` in the output.

### Terminal 3 — Playground (optional, for web testing)
```bash
cd /root/projects/livekit-voice-agent/agents-playground
pnpm start -H 0.0.0.0
```

### Terminal 4 — LiveKit SIP
```bash
docker rm -f livekit-sip 2>/dev/null
docker run -d --name livekit-sip \
  --network host \
  -v /root/projects/livekit-voice-agent/livekit/sip-config.yaml:/etc/sip.yaml \
  livekit/sip \
  --config /etc/sip.yaml
```

**Verify SIP is running:**
```bash
docker logs livekit-sip
```

**Expected output:**
```
INFO  sip  redis/redis.go  connecting to redis  {"addr": "localhost:6379"}
INFO  sip  sip/server.go   sip signaling listening on  {"port": 5060, "proto": "udp"}
INFO  sip  sip/server.go   sip signaling listening on  {"port": 5060, "proto": "tcp"}
```

> **⚠️ If you see `redis configuration is required`:** Your `sip-config.yaml` is missing the `redis` section. See [Reference — All Config Files](#reference--all-config-files).

---

## Step 11: Test the Phone Call

1. **Call your Twilio number** from a verified phone number
   - Example: Dial `+1 774 500 7904` from your mobile
2. **Wait 2-5 seconds** — the call connects through Twilio → SIP → LiveKit → Agent
3. **The agent should start speaking**

### What to Check If It Works:
- Terminal 2 (agent) shows room join and agent activity
- `docker logs livekit-sip` shows SIP INVITE received
- Terminal 1 (LiveKit) shows room creation

### Quick Test from VPS (No Phone Needed):
```bash
# List active rooms (should show "phone-call" during a call)
lk room list --url http://127.0.0.1:7880
```

---

## Complete Service Startup Checklist

Use this checklist every time you restart services:

```
1. [ ] Redis running:           systemctl status redis-server
2. [ ] LiveKit Server running:  ./livekit-server --config livekit-config.yaml
3. [ ] Agent running:           python3.11 agent.py dev (shows "registered worker")
4. [ ] SIP running:             docker logs livekit-sip (shows "listening on port 5060")
5. [ ] Firewall open:           ufw status (5060, 7880, 7881, 50000-60000)
6. [ ] Twilio trunk configured: Origination URI = sip:YOUR_IP:5060;transport=udp
7. [ ] Twilio number linked:    Number associated with trunk
8. [ ] Caller verified:         Your phone number in Verified Caller IDs
```

---

## Troubleshooting

### Problem: "sip not connected (redis required)"
**When:** Running `lk sip inbound create` or `lk sip dispatch create`
**Cause:** LiveKit Server is running in `--dev` mode (no Redis)
**Fix:** Start LiveKit Server with `--config livekit-config.yaml` that includes the `redis` section

### Problem: "redis configuration is required" (SIP Docker)
**When:** Starting the SIP Docker container
**Cause:** `sip-config.yaml` is missing the `redis` section
**Fix:** Ensure your `sip-config.yaml` has:
```yaml
redis:
  address: localhost:6379
```

### Problem: Twilio Error 21264 — 'From' phone number not verified
**When:** Calling the Twilio number from an unverified phone
**Cause:** Twilio trial accounts only accept calls from verified numbers
**Fix:** Go to Twilio Console → Phone Numbers → Verified Caller IDs → Add your phone number

### Problem: Call connects but no agent speaks
**When:** Phone rings, call is answered, but silence
**Possible causes:**
1. Agent (Terminal 2) is not running or didn't show "registered worker"
2. Agent crashed — check Terminal 2 for errors
3. LiveKit Server isn't running — check Terminal 1

**Debug:**
```bash
# Check if agent is registered
lk room list --url http://127.0.0.1:7880

# Check SIP logs for errors
docker logs --tail 50 livekit-sip

# Check agent logs
# Look at Terminal 2 output
```

### Problem: No SIP traffic reaching VPS (SIP logs show nothing)
**When:** You call but `docker logs livekit-sip` shows no new entries
**Possible causes:**
1. Twilio trunk Origination URI is wrong
2. Port 5060 is blocked by firewall
3. Phone number not associated with the SIP trunk
4. Twilio still routing to webhook instead of SIP trunk

**Fix:**
```bash
# Check port 5060 is open and listening
ss -ulnp | grep 5060
ss -tlnp | grep 5060

# Check UFW
ufw status | grep 5060

# Test from external machine
# On your local machine:
# curl -v --connect-timeout 5 sip://YOUR_VPS_IP:5060
```

Then verify in Twilio:
1. Trunks → Your trunk → Origination → URI matches `sip:YOUR_IP:5060;transport=udp`
2. Trunks → Your trunk → Numbers → Your number is listed
3. Phone Numbers → Your number → Voice Configuration = SIP Trunk (not Webhook)

### Problem: Call immediately disconnects or busy signal
**When:** Phone plays busy tone or disconnects instantly
**Cause:** SIP service is not running or not reachable
**Fix:**
```bash
# Is SIP container running?
docker ps | grep livekit-sip

# If not running, check why it stopped
docker logs livekit-sip

# Restart SIP
docker rm -f livekit-sip
docker run -d --name livekit-sip \
  --network host \
  -v /root/projects/livekit-voice-agent/livekit/sip-config.yaml:/etc/sip.yaml \
  livekit/sip \
  --config /etc/sip.yaml
```

### Problem: "secret is too short" error from LiveKit Server
**When:** Starting LiveKit Server
**Cause:** The API secret is shorter than 32 characters
**Impact:** Warning only — server still starts. For production, use a longer secret.
**Fix for production:**
```yaml
# In livekit-config.yaml, use a longer secret:
keys:
  your_api_key: your_very_long_secret_at_least_32_characters_here
```
Then update `.env` files for agent and playground to match.

### Problem: SIP container exits immediately
**When:** `docker ps` doesn't show the container
**Debug:**
```bash
docker logs livekit-sip
```
Common causes:
- Invalid YAML in `sip-config.yaml` — check indentation
- Redis not running — `systemctl start redis-server`
- Wrong `ws_url` — should be `ws://localhost:7880`

### Problem: Agent shows "failed to connect to livekit"
**When:** Agent (Terminal 2) shows repeated connection errors
**Cause:** Agent `.env` has wrong `LIVEKIT_URL`
**Fix:** Agent `.env` should have:
```
LIVEKIT_URL=ws://localhost:7880
```
NOT `wss://landphoneai.duckdns.org` (that's only for the browser playground).

---

## Reference — All Config Files

### File 1: LiveKit Server Config
**Path:** `/root/projects/livekit-voice-agent/livekit/livekit-config.yaml`
```yaml
port: 7880
bind_addresses:
  - 0.0.0.0
rtc:
  tcp_port: 7881
  port_range_start: 50000
  port_range_end: 60000
  use_external_ip: true
redis:
  address: localhost:6379
keys:
  devkey: secret
```

### File 2: SIP Service Config
**Path:** `/root/projects/livekit-voice-agent/livekit/sip-config.yaml`
```yaml
api_key: devkey
api_secret: secret
ws_url: ws://localhost:7880
redis:
  address: localhost:6379
sip:
  port: 5060
logging:
  level: info
```

### File 3: Agent .env (relevant SIP lines)
**Path:** `/root/projects/livekit-voice-agent/bangla-voice-agent/.env`
```env
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
```

### File 4: Playground .env.local (for web access)
**Path:** `/root/projects/livekit-voice-agent/agents-playground/.env.local`
```env
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
NEXT_PUBLIC_LIVEKIT_URL=wss://yourdomain.com
```

> **📌 NOTE:** Agent connects locally (`ws://localhost:7880`), browser connects via domain (`wss://yourdomain.com`).

---

## Reference — All Commands Cheat Sheet

### Service Management
```bash
# Start Redis
systemctl start redis-server

# Start LiveKit Server
cd /root/projects/livekit-voice-agent/livekit
./livekit-server --config livekit-config.yaml

# Start Agent
cd /root/projects/livekit-voice-agent/bangla-voice-agent
source .venv/bin/activate
python3.11 agent.py dev

# Start SIP
docker rm -f livekit-sip 2>/dev/null
docker run -d --name livekit-sip \
  --network host \
  -v /root/projects/livekit-voice-agent/livekit/sip-config.yaml:/etc/sip.yaml \
  livekit/sip \
  --config /etc/sip.yaml

# Start Playground
cd /root/projects/livekit-voice-agent/agents-playground
pnpm start -H 0.0.0.0
```

### SIP Trunk Management
```bash
# List inbound trunks
lk sip inbound list --url http://127.0.0.1:7880

# Create inbound trunk
lk sip inbound create --name "Twilio Inbound" --numbers "+1XXXXXXXXXX" --url http://127.0.0.1:7880

# Delete inbound trunk
lk sip inbound delete ST_xxxxxxxxxxxx --url http://127.0.0.1:7880

# List dispatch rules
lk sip dispatch list --url http://127.0.0.1:7880

# Create dispatch rule
lk sip dispatch create --name "Route to Agent" --direct "phone-call" --url http://127.0.0.1:7880

# Delete dispatch rule
lk sip dispatch delete SDR_xxxxxxxxxxxx --url http://127.0.0.1:7880
```

### Debugging
```bash
# Check SIP logs
docker logs --tail 50 livekit-sip

# Check SIP container status
docker ps | grep livekit-sip

# Check if ports are listening
ss -ulnp | grep 5060
ss -tlnp | grep 7880

# Check Redis
redis-cli ping

# Check firewall
ufw status

# List active LiveKit rooms
lk room list --url http://127.0.0.1:7880

# Restart SIP container
docker restart livekit-sip
```

---

## Changing Phone Numbers or VPS

### Scenario A: New Phone Number (Same VPS)

1. Buy new number in Twilio
2. Associate it with your existing SIP trunk (Trunks → Numbers → Add)
3. Delete old LiveKit inbound trunk: `lk sip inbound delete ST_xxx --url http://127.0.0.1:7880`
4. Create new one: `lk sip inbound create --name "New Number" --numbers "+1NEWXXXXXXX" --url http://127.0.0.1:7880`
5. If trial account, verify new caller numbers

### Scenario B: New VPS (Same Phone Number)

1. Set up new VPS following Steps 1-4 of this guide
2. Update Twilio trunk Origination URI to new VPS IP:
   - Trunks → Your trunk → Origination → Edit URI → `sip:NEW_VPS_IP:5060;transport=udp`
3. Create SIP inbound trunk and dispatch rule on new VPS (Steps 7-8)
4. Open firewall ports on new VPS (Step 9)
5. Start all services (Step 10)

### Scenario C: Different SIP Provider (Not Twilio)

The LiveKit SIP side stays the same. You only need to:
1. Set up the new provider's SIP trunk pointing to `sip:YOUR_VPS_IP:5060;transport=udp`
2. Associate a phone number with that trunk
3. Update the LiveKit inbound trunk with the new number:
   ```bash
   lk sip inbound create --name "New Provider" --numbers "+1XXXXXXXXXX" --url http://127.0.0.1:7880
   ```

---

## Cost Reference

### Twilio (Trial)
- Trial credit: **$15 free**
- US number: ~$1.15/month
- Inbound calls: ~$0.0085/min
- Outbound to Bangladesh: ~$0.04/min

### Twilio (Paid)
- Same pricing, no verified caller restriction
- Upgrade when ready for production

### Alternative Providers
| Provider | Inbound/min | Outbound to BD/min | Notes |
|----------|-------------|-------------------|-------|
| Twilio | $0.0085 | $0.04 | Most documented |
| Telnyx | $0.003 | $0.03 | Cheaper, good SIP support |
| Vonage | $0.0039 | $0.04 | Also works with LiveKit SIP |
| DIDWW | Varies | Varies | Has Bangladesh numbers |

---

> **Last updated:** February 2026
> **Tested on:** Contabo VPS, Ubuntu 24.04, LiveKit 1.9.11, LiveKit SIP (Docker), Twilio Elastic SIP Trunking
