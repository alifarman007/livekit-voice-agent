# SIP Management Tool — User Manual

> **File:** `sip-manage.sh`
> **Location:** Project root `/root/projects/livekit-voice-agent/sip-manage.sh`
> **Purpose:** One-command management of phone numbers, SIP providers, and SIP services

---

## Table of Contents

1. [Installation](#installation)
2. [First-Time Setup](#first-time-setup)
3. [All Commands Reference](#all-commands-reference)
4. [Common Workflows](#common-workflows)
5. [Provider Guides](#provider-guides)
6. [Troubleshooting](#troubleshooting)
7. [Configuration](#configuration)

---

## Installation

### Step 1: Copy files to VPS

From your local machine (Git Bash):

```bash
cd /c/Python_Projects/Voice_agent
git add sip-manage.sh sip/
git commit -m "Add SIP management tool"
git push
```

On VPS:

```bash
cd /root/projects/livekit-voice-agent
git pull
```

### Step 2: Make script executable

```bash
chmod +x sip-manage.sh
```

### Step 3: Update VPS IP (if different from default)

Edit the top of `sip-manage.sh`:

```bash
nano sip-manage.sh
```

Change this line to your VPS IP:

```bash
VPS_IP="161.97.98.67"    # ← Change this to your VPS IP
```

Save and exit (`Ctrl+X` → `Y` → `Enter`).

### Step 4: Verify installation

```bash
./sip-manage.sh help
```

You should see the help menu with all available commands.

---

## First-Time Setup

If this is a fresh VPS or you've never configured SIP before, run the interactive setup wizard:

```bash
./sip-manage.sh setup
```

The wizard will:
1. Check all prerequisites (Redis, Docker, LiveKit Server, CLI)
2. Create the dispatch rule (routes phone calls to agent)
3. Pull the SIP Docker image
4. Create/verify the SIP config file
5. Open firewall ports (5060/udp, 5060/tcp)
6. Start the SIP Docker container
7. Ask for your phone number and configure it

After setup completes, configure your SIP provider (see [Provider Guides](#provider-guides)), then call your number to test.

---

## All Commands Reference

### `status` — Health Dashboard

```bash
./sip-manage.sh status
```

Shows at a glance:
- Whether Redis, LiveKit Server, SIP container, and Voice Agent are running
- All active phone numbers with their trunk IDs
- Current dispatch rules
- Last SIP log entries

**When to use:** Anytime you want a quick overview of your system.

---

### `add-number` — Add a Phone Number

```bash
./sip-manage.sh add-number +17745007904
./sip-manage.sh add-number +8801712345678
```

Adds a new phone number to LiveKit SIP. After running this, the number will be recognized when calls arrive at your VPS.

**Requirements:**
- Number must start with `+` followed by 7-15 digits
- LiveKit Server must be running
- The number must already be purchased from your SIP provider
- Your SIP provider must be configured to forward calls to `sip:YOUR_VPS_IP:5060;transport=udp`

**Example output:**
```
  ✅ Number added successfully!

  Number:   +8801712345678
  Trunk ID: ST_abc123xyz

  ⚠️  REMINDER: Make sure this number is configured in your
     SIP provider's dashboard to forward to:
     sip:161.97.98.67:5060;transport=udp
```

---

### `remove-number` — Remove a Phone Number

```bash
./sip-manage.sh remove-number +17745007904
```

Removes a phone number from LiveKit SIP. Asks for confirmation before removing.

**Example:**
```
  Number:   +17745007904
  Trunk ID: ST_qBzKcnW2gqL6

  ⚠️  Are you sure you want to remove this number? (y/N): y
  ✅ Number +17745007904 removed (Trunk: ST_qBzKcnW2gqL6)
```

---

### `replace-number` — Swap Numbers (Zero Downtime)

```bash
./sip-manage.sh replace-number +17745007904 +8801712345678
```

Safely swaps one number for another. Adds the new number FIRST, then removes the old one — so there's no period where no number is active.

**When to use:** Switching from a US test number to a Bangladesh production number.

---

### `list-numbers` — Show All Active Numbers

```bash
./sip-manage.sh list-numbers
```

Displays the full table of all configured inbound SIP trunks with their IDs, names, and associated numbers.

---

### `set-provider` — Provider Setup Instructions

```bash
./sip-manage.sh set-provider              # List all providers
./sip-manage.sh set-provider twilio       # Twilio instructions
./sip-manage.sh set-provider hottelecom   # HotTelecom instructions
./sip-manage.sh set-provider freezvon     # Freezvon instructions
./sip-manage.sh set-provider telnyx       # Telnyx instructions
./sip-manage.sh set-provider vonage       # Vonage instructions
./sip-manage.sh set-provider custom       # Generic instructions
```

Shows step-by-step setup instructions for each SIP provider, automatically filled in with your VPS IP address.

**This does NOT change any configuration on your VPS.** It only prints instructions for what to do on the provider's dashboard. Your VPS-side SIP setup works with ALL providers — only the provider dashboard setup differs.

---

### `test` — Full Connectivity Test

```bash
./sip-manage.sh test
```

Runs a comprehensive diagnostic checking:
- Prerequisites (Redis, Docker, LiveKit CLI)
- Services (LiveKit Server, SIP container, ports)
- Firewall (5060/udp, 5060/tcp)
- SIP configuration (config file, Redis, dispatch rules, inbound trunks)

Each check shows ✅ or ❌ with a fix command if it fails.

**When to use:** After setup, before first call, or when debugging problems.

---

### `restart` — Restart SIP Container

```bash
./sip-manage.sh restart
```

Stops and restarts the LiveKit SIP Docker container. Useful after changing the SIP config file or when the container has issues.

---

### `logs` — View SIP Logs

```bash
./sip-manage.sh logs           # Last 20 lines
./sip-manage.sh logs 50        # Last 50 lines
./sip-manage.sh logs follow    # Live tail (Ctrl+C to stop)
```

**When to use:**
- `logs follow` — Run this in a terminal while making a test call to see SIP activity in real-time
- `logs 50` — Check recent activity after a failed call

---

### `setup` — Interactive First-Time Wizard

```bash
./sip-manage.sh setup
```

Full walkthrough described in [First-Time Setup](#first-time-setup) above.

---

### `help` — Show Help

```bash
./sip-manage.sh help
```

Shows all available commands with examples.

---

## Common Workflows

### Workflow 1: Brand New VPS Setup

```bash
# 1. Run the setup wizard
./sip-manage.sh setup

# 2. Follow provider instructions
./sip-manage.sh set-provider twilio

# 3. After configuring provider, test connectivity
./sip-manage.sh test

# 4. Start watching logs and make a test call
./sip-manage.sh logs follow
# (In another phone, call your number)
```

### Workflow 2: Add a Second Phone Number

```bash
# 1. Buy number from your SIP provider
# 2. Configure it in provider dashboard to point to your VPS
# 3. Add to LiveKit
./sip-manage.sh add-number +8801XXXXXXXXX

# 4. Verify
./sip-manage.sh list-numbers
```

### Workflow 3: Switch from Twilio (US) to HotTelecom (Bangladesh)

```bash
# 1. Buy BD number from HotTelecom
# 2. Configure HotTelecom
./sip-manage.sh set-provider hottelecom
# (Follow the printed instructions)

# 3. Replace the number
./sip-manage.sh replace-number +17745007904 +880XXXXXXXXXX

# 4. Test
./sip-manage.sh test
./sip-manage.sh logs follow
# (Call the new BD number)
```

### Workflow 4: Move to a New VPS

```bash
# On NEW VPS:

# 1. Clone repo, install dependencies, set up agent
# 2. Edit VPS_IP in sip-manage.sh to new VPS IP
nano sip-manage.sh
# Change: VPS_IP="NEW.IP.HERE"

# 3. Run setup wizard
./sip-manage.sh setup

# 4. Update SIP provider dashboard:
#    Change origination URI to new VPS IP
./sip-manage.sh set-provider twilio
# (Follow instructions to update URI)

# 5. Add your number
./sip-manage.sh add-number +17745007904

# 6. Test
./sip-manage.sh test
```

### Workflow 5: Debug a Failed Call

```bash
# 1. Check everything at once
./sip-manage.sh status

# 2. Run diagnostics
./sip-manage.sh test

# 3. Watch logs while making a call
./sip-manage.sh logs follow
# (Make the call from your phone)

# 4. If SIP container isn't working
./sip-manage.sh restart
./sip-manage.sh logs
```

### Workflow 6: Daily Operations

```bash
# Morning check
./sip-manage.sh status

# If something's wrong
./sip-manage.sh test

# Restart if needed
./sip-manage.sh restart
```

---

## Provider Guides

### Which Provider Should I Use?

| Provider | Bangladesh +880 | Cheapest For | Best For |
|----------|----------------|-------------|----------|
| **Twilio** | ❌ | US/EU numbers | Quick setup, testing, well documented |
| **Telnyx** | ❌ | US/EU numbers (cheaper than Twilio) | Cost savings on US/EU calls |
| **HotTelecom** | ✅ | Bangladesh numbers | BD production deployment |
| **Freezvon** | ✅ | Bangladesh numbers | BD production with outbound calls |
| **Vonage** | ❌ | Outbound to BD | Agent calling BD numbers |

### For Bangladesh Production

**Recommended path:**
1. **Start with Twilio** (US number) for development and testing — easiest to set up
2. **Move to HotTelecom or Freezvon** for production — they have actual +880 numbers

### Viewing Provider Instructions

```bash
./sip-manage.sh set-provider twilio
./sip-manage.sh set-provider hottelecom
./sip-manage.sh set-provider freezvon
./sip-manage.sh set-provider telnyx
./sip-manage.sh set-provider vonage
./sip-manage.sh set-provider custom
```

Each guide shows step-by-step instructions with your VPS IP automatically filled in.

---

## Troubleshooting

### "Command not found" when running sip-manage.sh

```bash
chmod +x sip-manage.sh
./sip-manage.sh help
```

### SIP container won't start

```bash
# Check logs
docker logs livekit-sip

# Common fix: Redis not running
systemctl start redis-server

# Common fix: Config file missing redis section
cat /root/projects/livekit-voice-agent/livekit/sip-config.yaml
# Should contain:
# redis:
#   address: localhost:6379
```

### Calls don't reach VPS (no SIP logs)

1. Check provider dashboard — is origination URI correct?
   ```
   sip:YOUR_VPS_IP:5060;transport=udp
   ```
2. Check firewall: `./sip-manage.sh test`
3. Check port listening: `ss -ulnp | grep 5060`
4. For Twilio trial: Is caller in Verified Caller IDs?

### Call connects but agent doesn't speak

1. Is the voice agent running?
   ```bash
   ./sip-manage.sh status
   ```
2. Check agent terminal for errors
3. Is the dispatch rule configured?
   ```bash
   ./sip-manage.sh test
   ```

### "redis configuration is required" error

Your `sip-config.yaml` is missing the redis section. Fix:

```bash
# Edit the config
nano /root/projects/livekit-voice-agent/livekit/sip-config.yaml

# Make sure it contains:
# redis:
#   address: localhost:6379

# Restart SIP
./sip-manage.sh restart
```

---

## Configuration

### Script Configuration

Edit the top of `sip-manage.sh` to match your setup:

```bash
LIVEKIT_URL="http://127.0.0.1:7880"          # LiveKit Server URL
SIP_CONFIG_PATH="/root/projects/.../sip-config.yaml"  # SIP config location
VPS_IP="161.97.98.67"                         # Your VPS public IP
SIP_PORT="5060"                               # SIP port (usually 5060)
SIP_CONTAINER_NAME="livekit-sip"              # Docker container name
SIP_DOCKER_IMAGE="livekit/sip"                # Docker image
```

### File Structure

```
livekit-voice-agent/
├── sip-manage.sh              # Main management script
├── sip/
│   └── providers/             # Provider setup templates
│       ├── twilio.txt         # Twilio instructions
│       ├── telnyx.txt         # Telnyx instructions
│       ├── hottelecom.txt     # HotTelecom instructions (has BD +880)
│       ├── freezvon.txt       # Freezvon instructions (has BD +880)
│       ├── vonage.txt         # Vonage instructions
│       └── custom.txt         # Generic SIP provider
├── sip-manage-manual.md       # This manual
├── siptrunk_runguide.md       # Detailed first-time SIP setup guide
└── livekit/
    ├── sip-config.yaml        # SIP service configuration
    └── livekit-config.yaml    # LiveKit server configuration
```

### Adding a New Provider Template

Create a new file in `sip/providers/`:

```bash
nano sip/providers/myprovider.txt
```

Use `{{VPS_IP}}` and `{{SIP_PORT}}` as placeholders — they get auto-replaced when displayed:

```
  Provider: My Provider
  Website:  https://myprovider.com

  Step 1: ...
  Step 2: Forward calls to sip:{{VPS_IP}}:{{SIP_PORT}};transport=udp
  Step 3: ...
```

Then use it:

```bash
./sip-manage.sh set-provider myprovider
```

---

> **Last updated:** February 2026
