#!/bin/bash

# ============================================================
# SIP Management Tool for LiveKit Voice Agent
# One-command SIP trunk management — no CLI memorization needed
# ============================================================

# --- Configuration (edit these for your setup) ---
LIVEKIT_URL="http://127.0.0.1:7880"
SIP_CONFIG_PATH="/root/projects/livekit-voice-agent/livekit/sip-config.yaml"
VPS_IP="161.97.98.67"
SIP_PORT="5060"
SIP_CONTAINER_NAME="livekit-sip"
SIP_DOCKER_IMAGE="livekit/sip"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROVIDERS_DIR="$SCRIPT_DIR/sip/providers"
# -------------------------------------------------

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Icons
CHECK="✅"
CROSS="❌"
WARN="⚠️"
INFO="ℹ️"

# ============================================================
# Helper Functions
# ============================================================

print_header() {
    echo ""
    echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${CYAN}  $1${NC}"
    echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_section() {
    echo ""
    echo -e "${BOLD}$1${NC}"
    echo -e "───────────────────────────────────────────────"
}

ok() {
    echo -e "  ${GREEN}${CHECK} $1${NC}"
}

fail() {
    echo -e "  ${RED}${CROSS} $1${NC}"
}

warn() {
    echo -e "  ${YELLOW}${WARN}  $1${NC}"
}

info() {
    echo -e "  ${BLUE}${INFO}  $1${NC}"
}

validate_number() {
    local number="$1"
    if [[ ! "$number" =~ ^\+[0-9]{7,15}$ ]]; then
        echo -e "${RED}Error: Invalid phone number format.${NC}"
        echo "  Must start with + followed by 7-15 digits."
        echo "  Example: +17745007904 or +8801XXXXXXXXX"
        return 1
    fi
    return 0
}

check_lk_cli() {
    if ! command -v lk &> /dev/null; then
        echo -e "${RED}Error: LiveKit CLI (lk) not found.${NC}"
        echo "  Install: curl -sSL https://get.livekit.io/cli | bash"
        return 1
    fi
    return 0
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker not found.${NC}"
        echo "  Install: apt install -y docker.io"
        return 1
    fi
    return 0
}

get_trunk_id_for_number() {
    local number="$1"
    lk sip inbound list --url "$LIVEKIT_URL" 2>/dev/null | grep "$number" | awk '{print $2}'
}

# ============================================================
# Command: status
# ============================================================

cmd_status() {
    print_header "SIP Management — Status"

    print_section "Services"

    # Redis
    if redis-cli ping &>/dev/null; then
        ok "Redis:          Running"
    else
        fail "Redis:          Not running"
    fi

    # LiveKit Server
    if ss -tlnp 2>/dev/null | grep -q ":7880"; then
        ok "LiveKit Server: Running (port 7880)"
    else
        fail "LiveKit Server: Not running"
    fi

    # SIP Container
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${SIP_CONTAINER_NAME}$"; then
        ok "SIP Container:  Running (port $SIP_PORT)"
    else
        fail "SIP Container:  Not running"
    fi

    # Voice Agent
    if ps aux 2>/dev/null | grep -v grep | grep -q "agent.py"; then
        ok "Voice Agent:    Running"
    else
        fail "Voice Agent:    Not running"
    fi

    # Firewall
    if ufw status 2>/dev/null | grep -q "5060"; then
        ok "Firewall 5060:  Open"
    else
        warn "Firewall 5060:  Not found in UFW rules"
    fi

    print_section "Active Phone Numbers"

    local trunk_list
    trunk_list=$(lk sip inbound list --url "$LIVEKIT_URL" 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$trunk_list" ]; then
        echo "$trunk_list" | grep -E "ST_" | while IFS='│' read -r _ trunk_id _ name _ numbers _; do
            trunk_id=$(echo "$trunk_id" | xargs)
            name=$(echo "$name" | xargs)
            numbers=$(echo "$numbers" | xargs)
            if [ -n "$trunk_id" ]; then
                echo -e "  ${GREEN}📞 $numbers${NC}  (Trunk: $trunk_id, Name: $name)"
            fi
        done
    else
        warn "No inbound trunks found or LiveKit not reachable"
    fi

    print_section "Dispatch Rules"

    local dispatch_list
    dispatch_list=$(lk sip dispatch list --url "$LIVEKIT_URL" 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$dispatch_list" ]; then
        echo "$dispatch_list" | grep -E "SDR_" | while IFS='│' read -r _ rule_id _ name _ _ _ room _; do
            rule_id=$(echo "$rule_id" | xargs)
            name=$(echo "$name" | xargs)
            room=$(echo "$room" | xargs)
            if [ -n "$rule_id" ]; then
                echo -e "  ${GREEN}📋 $rule_id${NC} → room \"$room\" ($name)"
            fi
        done
    else
        warn "No dispatch rules found"
    fi

    print_section "SIP Last Activity"

    docker logs --tail 3 "$SIP_CONTAINER_NAME" 2>/dev/null | tail -3 | while read -r line; do
        echo "  $line"
    done

    echo ""
}

# ============================================================
# Command: add-number
# ============================================================

cmd_add_number() {
    local number="$1"

    print_header "SIP Management — Add Number"

    if [ -z "$number" ]; then
        echo -e "${RED}Usage: sip-manage.sh add-number +XXXXXXXXXXXX${NC}"
        echo ""
        echo "  Example: sip-manage.sh add-number +17745007904"
        echo "  Example: sip-manage.sh add-number +8801712345678"
        return 1
    fi

    validate_number "$number" || return 1
    check_lk_cli || return 1

    info "Adding number $number..."
    echo ""

    local output
    output=$(lk sip inbound create --name "SIP-$number" --numbers "$number" --url "$LIVEKIT_URL" 2>&1)

    if [ $? -eq 0 ]; then
        local trunk_id
        trunk_id=$(echo "$output" | grep -oP 'ST_\w+')
        ok "Number added successfully!"
        echo ""
        echo -e "  Number:   ${BOLD}$number${NC}"
        echo -e "  Trunk ID: ${BOLD}$trunk_id${NC}"
        echo ""
        echo -e "  ${YELLOW}${WARN}  REMINDER: Make sure this number is configured in your${NC}"
        echo -e "  ${YELLOW}   SIP provider's dashboard to forward to:${NC}"
        echo -e "  ${YELLOW}   sip:${VPS_IP}:${SIP_PORT};transport=udp${NC}"
    else
        fail "Failed to add number"
        echo "  $output"
    fi
    echo ""
}

# ============================================================
# Command: remove-number
# ============================================================

cmd_remove_number() {
    local number="$1"

    print_header "SIP Management — Remove Number"

    if [ -z "$number" ]; then
        echo -e "${RED}Usage: sip-manage.sh remove-number +XXXXXXXXXXXX${NC}"
        return 1
    fi

    validate_number "$number" || return 1
    check_lk_cli || return 1

    # Find trunk ID for this number
    info "Looking up trunk for $number..."

    local trunk_id
    trunk_id=$(get_trunk_id_for_number "$number")

    if [ -z "$trunk_id" ]; then
        fail "No trunk found for number $number"
        echo "  Run 'sip-manage.sh list-numbers' to see all active numbers."
        return 1
    fi

    echo ""
    echo -e "  Number:   ${BOLD}$number${NC}"
    echo -e "  Trunk ID: ${BOLD}$trunk_id${NC}"
    echo ""
    echo -en "  ${YELLOW}Are you sure you want to remove this number? (y/N): ${NC}"
    read -r confirm

    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        local output
        output=$(lk sip inbound delete "$trunk_id" --url "$LIVEKIT_URL" 2>&1)
        if [ $? -eq 0 ]; then
            ok "Number $number removed (Trunk: $trunk_id)"
            echo ""
            echo -e "  ${YELLOW}${WARN}  Don't forget to also remove this number from your${NC}"
            echo -e "  ${YELLOW}   SIP provider's dashboard if no longer needed.${NC}"
        else
            fail "Failed to remove trunk"
            echo "  $output"
        fi
    else
        info "Cancelled — no changes made."
    fi
    echo ""
}

# ============================================================
# Command: replace-number
# ============================================================

cmd_replace_number() {
    local old_number="$1"
    local new_number="$2"

    print_header "SIP Management — Replace Number"

    if [ -z "$old_number" ] || [ -z "$new_number" ]; then
        echo -e "${RED}Usage: sip-manage.sh replace-number +OLD_NUMBER +NEW_NUMBER${NC}"
        echo ""
        echo "  Example: sip-manage.sh replace-number +17745007904 +8801712345678"
        return 1
    fi

    validate_number "$old_number" || return 1
    validate_number "$new_number" || return 1
    check_lk_cli || return 1

    echo ""
    echo -e "  Old: ${RED}$old_number${NC}"
    echo -e "  New: ${GREEN}$new_number${NC}"
    echo ""

    # Step 1: Add new number first (no downtime)
    info "Step 1/2: Adding new number $new_number..."
    local add_output
    add_output=$(lk sip inbound create --name "SIP-$new_number" --numbers "$new_number" --url "$LIVEKIT_URL" 2>&1)

    if [ $? -ne 0 ]; then
        fail "Failed to add new number. Old number unchanged."
        echo "  $add_output"
        return 1
    fi

    local new_trunk_id
    new_trunk_id=$(echo "$add_output" | grep -oP 'ST_\w+')
    ok "New number added (Trunk: $new_trunk_id)"

    # Step 2: Remove old number
    info "Step 2/2: Removing old number $old_number..."
    local old_trunk_id
    old_trunk_id=$(get_trunk_id_for_number "$old_number")

    if [ -n "$old_trunk_id" ]; then
        lk sip inbound delete "$old_trunk_id" --url "$LIVEKIT_URL" &>/dev/null
        if [ $? -eq 0 ]; then
            ok "Old number removed (Trunk: $old_trunk_id)"
        else
            warn "Could not remove old trunk $old_trunk_id — remove manually"
        fi
    else
        warn "Old number trunk not found — may already be removed"
    fi

    echo ""
    ok "Number replaced successfully!"
    echo ""
    echo -e "  ${YELLOW}${WARN}  REMINDER: Update your SIP provider dashboard:${NC}"
    echo -e "  ${YELLOW}   1. Associate new number with trunk → sip:${VPS_IP}:${SIP_PORT};transport=udp${NC}"
    echo -e "  ${YELLOW}   2. Remove old number association if no longer needed${NC}"
    echo ""
}

# ============================================================
# Command: list-numbers
# ============================================================

cmd_list_numbers() {
    print_header "SIP Management — Active Numbers"

    check_lk_cli || return 1

    echo ""
    lk sip inbound list --url "$LIVEKIT_URL" 2>/dev/null

    if [ $? -ne 0 ]; then
        fail "Could not connect to LiveKit server at $LIVEKIT_URL"
        echo "  Is LiveKit Server running?"
    fi
    echo ""
}

# ============================================================
# Command: set-provider
# ============================================================

cmd_set_provider() {
    local provider="$1"

    print_header "SIP Management — Provider Setup Guide"

    if [ -z "$provider" ]; then
        echo ""
        echo "  Available providers:"
        echo ""
        echo -e "    ${CYAN}twilio${NC}      — Twilio Elastic SIP Trunking"
        echo -e "    ${CYAN}telnyx${NC}      — Telnyx SIP Trunking"
        echo -e "    ${CYAN}hottelecom${NC}  — HotTelecom (has Bangladesh +880)"
        echo -e "    ${CYAN}freezvon${NC}    — Freezvon (has Bangladesh +880)"
        echo -e "    ${CYAN}vonage${NC}      — Vonage SIP Trunking"
        echo -e "    ${CYAN}custom${NC}      — Any SIP trunk provider"
        echo ""
        echo -e "  Usage: ${BOLD}sip-manage.sh set-provider <name>${NC}"
        return 0
    fi

    local provider_file="$PROVIDERS_DIR/${provider}.txt"

    if [ ! -f "$provider_file" ]; then
        fail "Unknown provider: $provider"
        echo "  Run 'sip-manage.sh set-provider' to see available providers."
        return 1
    fi

    echo ""
    echo -e "  ${BOLD}Your VPS SIP Endpoint:${NC}"
    echo -e "  ${GREEN}sip:${VPS_IP}:${SIP_PORT};transport=udp${NC}"
    echo ""
    echo -e "  ${BOLD}Setup Instructions for ${CYAN}${provider}${NC}${BOLD}:${NC}"
    echo "  ─────────────────────────────────────────"
    echo ""

    # Replace {{VPS_IP}} and {{SIP_PORT}} placeholders in template
    sed "s/{{VPS_IP}}/${VPS_IP}/g; s/{{SIP_PORT}}/${SIP_PORT}/g" "$provider_file"

    echo ""
    echo "  ─────────────────────────────────────────"
    echo ""
    echo -e "  ${BOLD}After provider setup, run:${NC}"
    echo -e "  ${GREEN}sip-manage.sh add-number +XXXXXXXXXXXX${NC}"
    echo ""
}

# ============================================================
# Command: test
# ============================================================

cmd_test() {
    print_header "SIP Management — Connectivity Test"

    local all_pass=true

    print_section "1. Prerequisites"

    # Redis
    if redis-cli ping &>/dev/null; then
        ok "Redis is running"
    else
        fail "Redis is NOT running"
        echo "    Fix: systemctl start redis-server"
        all_pass=false
    fi

    # Docker
    if command -v docker &>/dev/null; then
        ok "Docker is installed"
    else
        fail "Docker is NOT installed"
        echo "    Fix: apt install -y docker.io"
        all_pass=false
    fi

    # LiveKit CLI
    if command -v lk &>/dev/null; then
        ok "LiveKit CLI (lk) is installed"
    else
        fail "LiveKit CLI is NOT installed"
        echo "    Fix: curl -sSL https://get.livekit.io/cli | bash"
        all_pass=false
    fi

    print_section "2. Services"

    # LiveKit Server
    if ss -tlnp 2>/dev/null | grep -q ":7880"; then
        ok "LiveKit Server listening on port 7880"
    else
        fail "LiveKit Server NOT listening on port 7880"
        echo "    Fix: cd /root/projects/livekit-voice-agent/livekit && ./livekit-server --config livekit-config.yaml"
        all_pass=false
    fi

    # SIP Container
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${SIP_CONTAINER_NAME}$"; then
        ok "SIP container is running"
    else
        fail "SIP container is NOT running"
        echo "    Fix: sip-manage.sh restart"
        all_pass=false
    fi

    # SIP Port
    if ss -ulnp 2>/dev/null | grep -q ":5060"; then
        ok "SIP listening on UDP port 5060"
    else
        fail "SIP NOT listening on UDP port 5060"
        all_pass=false
    fi

    if ss -tlnp 2>/dev/null | grep -q ":5060"; then
        ok "SIP listening on TCP port 5060"
    else
        fail "SIP NOT listening on TCP port 5060"
        all_pass=false
    fi

    print_section "3. Firewall"

    if ufw status 2>/dev/null | grep -q "5060/udp.*ALLOW"; then
        ok "UFW allows 5060/udp"
    else
        fail "UFW does NOT allow 5060/udp"
        echo "    Fix: ufw allow 5060/udp"
        all_pass=false
    fi

    if ufw status 2>/dev/null | grep -q "5060/tcp.*ALLOW"; then
        ok "UFW allows 5060/tcp"
    else
        fail "UFW does NOT allow 5060/tcp"
        echo "    Fix: ufw allow 5060/tcp"
        all_pass=false
    fi

    print_section "4. SIP Configuration"

    # Config file exists
    if [ -f "$SIP_CONFIG_PATH" ]; then
        ok "SIP config file exists: $SIP_CONFIG_PATH"
    else
        fail "SIP config file missing: $SIP_CONFIG_PATH"
        all_pass=false
    fi

    # Redis in config
    if grep -q "redis" "$SIP_CONFIG_PATH" 2>/dev/null; then
        ok "Redis configured in SIP config"
    else
        fail "Redis NOT configured in SIP config"
        all_pass=false
    fi

    # Dispatch rule
    local dispatch_count
    dispatch_count=$(lk sip dispatch list --url "$LIVEKIT_URL" 2>/dev/null | grep -c "SDR_")
    if [ "$dispatch_count" -gt 0 ]; then
        ok "Dispatch rule exists ($dispatch_count rules)"
    else
        fail "No dispatch rules found"
        echo "    Fix: lk sip dispatch create --name \"Route to Agent\" --direct \"phone-call\" --url $LIVEKIT_URL"
        all_pass=false
    fi

    # Inbound trunks
    local trunk_count
    trunk_count=$(lk sip inbound list --url "$LIVEKIT_URL" 2>/dev/null | grep -c "ST_")
    if [ "$trunk_count" -gt 0 ]; then
        ok "Inbound trunk exists ($trunk_count numbers)"
    else
        warn "No inbound trunks — add a number with: sip-manage.sh add-number +XXX"
    fi

    print_section "Result"

    if $all_pass; then
        echo ""
        ok "All checks passed! SIP is ready for calls."
    else
        echo ""
        fail "Some checks failed. Fix the issues above and run test again."
    fi
    echo ""
}

# ============================================================
# Command: restart
# ============================================================

cmd_restart() {
    print_header "SIP Management — Restart SIP Service"

    check_docker || return 1

    info "Stopping SIP container..."
    docker rm -f "$SIP_CONTAINER_NAME" 2>/dev/null
    ok "Container stopped"

    info "Starting SIP container..."

    if [ ! -f "$SIP_CONFIG_PATH" ]; then
        fail "SIP config not found: $SIP_CONFIG_PATH"
        return 1
    fi

    docker run -d --name "$SIP_CONTAINER_NAME" \
        --network host \
        -v "$SIP_CONFIG_PATH:/etc/sip.yaml" \
        "$SIP_DOCKER_IMAGE" \
        --config /etc/sip.yaml &>/dev/null

    sleep 2

    if docker ps --format '{{.Names}}' | grep -q "^${SIP_CONTAINER_NAME}$"; then
        ok "SIP container started"
        echo ""
        info "Recent logs:"
        docker logs --tail 5 "$SIP_CONTAINER_NAME" 2>&1 | while read -r line; do
            echo "    $line"
        done
    else
        fail "SIP container failed to start"
        echo ""
        echo "  Logs:"
        docker logs "$SIP_CONTAINER_NAME" 2>&1 | while read -r line; do
            echo "    $line"
        done
    fi
    echo ""
}

# ============================================================
# Command: logs
# ============================================================

cmd_logs() {
    local arg="$1"

    if [ "$arg" = "follow" ] || [ "$arg" = "-f" ]; then
        echo -e "${CYAN}Following SIP logs (Ctrl+C to stop)...${NC}"
        echo ""
        docker logs -f "$SIP_CONTAINER_NAME" 2>&1
    else
        local lines="${arg:-20}"
        print_header "SIP Management — Logs (last $lines lines)"
        echo ""
        docker logs --tail "$lines" "$SIP_CONTAINER_NAME" 2>&1
        echo ""
    fi
}

# ============================================================
# Command: setup (interactive first-time wizard)
# ============================================================

cmd_setup() {
    print_header "SIP Management — First-Time Setup"

    echo ""
    echo -e "  ${BOLD}This wizard will set up SIP phone call support for your voice agent.${NC}"
    echo ""

    # Step 1: Check prerequisites
    print_section "Step 1: Checking Prerequisites"

    local prereq_pass=true

    if redis-cli ping &>/dev/null; then
        ok "Redis"
    else
        fail "Redis — run: apt install -y redis-server && systemctl start redis-server"
        prereq_pass=false
    fi

    if command -v docker &>/dev/null; then
        ok "Docker"
    else
        fail "Docker — run: apt install -y docker.io && systemctl start docker"
        prereq_pass=false
    fi

    if ss -tlnp 2>/dev/null | grep -q ":7880"; then
        ok "LiveKit Server"
    else
        fail "LiveKit Server — start it first in another terminal"
        prereq_pass=false
    fi

    if command -v lk &>/dev/null; then
        ok "LiveKit CLI"
    else
        fail "LiveKit CLI — run: curl -sSL https://get.livekit.io/cli | bash"
        prereq_pass=false
    fi

    if ! $prereq_pass; then
        echo ""
        fail "Fix prerequisites above and run setup again."
        return 1
    fi

    # Step 2: Check/create dispatch rule
    print_section "Step 2: Dispatch Rule"

    local dispatch_count
    dispatch_count=$(lk sip dispatch list --url "$LIVEKIT_URL" 2>/dev/null | grep -c "SDR_")

    if [ "$dispatch_count" -gt 0 ]; then
        ok "Dispatch rule already exists"
    else
        info "Creating dispatch rule..."
        lk sip dispatch create --name "Route to Agent" --direct "phone-call" --url "$LIVEKIT_URL" &>/dev/null
        if [ $? -eq 0 ]; then
            ok "Dispatch rule created (calls → room 'phone-call')"
        else
            fail "Failed to create dispatch rule"
            return 1
        fi
    fi

    # Step 3: Check/pull SIP Docker image
    print_section "Step 3: SIP Docker Image"

    if docker images "$SIP_DOCKER_IMAGE" --format '{{.Repository}}' 2>/dev/null | grep -q "livekit/sip"; then
        ok "SIP Docker image exists"
    else
        info "Pulling SIP Docker image (this may take a minute)..."
        docker pull "$SIP_DOCKER_IMAGE" &>/dev/null
        if [ $? -eq 0 ]; then
            ok "SIP image pulled"
        else
            fail "Failed to pull SIP image"
            return 1
        fi
    fi

    # Step 4: Check SIP config
    print_section "Step 4: SIP Configuration"

    if [ -f "$SIP_CONFIG_PATH" ]; then
        ok "SIP config exists: $SIP_CONFIG_PATH"
    else
        info "Creating SIP config..."
        cat > "$SIP_CONFIG_PATH" << 'SIPEOF'
api_key: devkey
api_secret: secret
ws_url: ws://localhost:7880
redis:
  address: localhost:6379
sip:
  port: 5060
logging:
  level: info
SIPEOF
        ok "SIP config created"
        warn "Update api_key and api_secret to match your LiveKit Server config!"
    fi

    # Step 5: Firewall
    print_section "Step 5: Firewall"

    if ! ufw status 2>/dev/null | grep -q "5060/udp.*ALLOW"; then
        ufw allow 5060/udp &>/dev/null
        ok "Opened port 5060/udp"
    else
        ok "Port 5060/udp already open"
    fi

    if ! ufw status 2>/dev/null | grep -q "5060/tcp.*ALLOW"; then
        ufw allow 5060/tcp &>/dev/null
        ok "Opened port 5060/tcp"
    else
        ok "Port 5060/tcp already open"
    fi

    # Step 6: Start SIP
    print_section "Step 6: Starting SIP Service"

    docker rm -f "$SIP_CONTAINER_NAME" 2>/dev/null

    docker run -d --name "$SIP_CONTAINER_NAME" \
        --network host \
        -v "$SIP_CONFIG_PATH:/etc/sip.yaml" \
        "$SIP_DOCKER_IMAGE" \
        --config /etc/sip.yaml &>/dev/null

    sleep 2

    if docker ps --format '{{.Names}}' | grep -q "^${SIP_CONTAINER_NAME}$"; then
        ok "SIP service running on port $SIP_PORT"
    else
        fail "SIP failed to start — check: docker logs $SIP_CONTAINER_NAME"
        return 1
    fi

    # Step 7: Add phone number
    print_section "Step 7: Phone Number"

    local trunk_count
    trunk_count=$(lk sip inbound list --url "$LIVEKIT_URL" 2>/dev/null | grep -c "ST_")

    if [ "$trunk_count" -gt 0 ]; then
        ok "Phone number(s) already configured"
    else
        echo ""
        echo -en "  Enter your phone number (e.g. +17745007904): "
        read -r user_number

        if [ -n "$user_number" ]; then
            if validate_number "$user_number"; then
                lk sip inbound create --name "SIP-$user_number" --numbers "$user_number" --url "$LIVEKIT_URL" &>/dev/null
                if [ $? -eq 0 ]; then
                    ok "Number $user_number added"
                else
                    fail "Failed to add number"
                fi
            fi
        else
            info "Skipped — add later with: sip-manage.sh add-number +XXX"
        fi
    fi

    # Done
    print_section "Setup Complete!"

    echo ""
    echo -e "  ${GREEN}${CHECK} SIP phone call support is ready!${NC}"
    echo ""
    echo -e "  ${BOLD}Your SIP endpoint:${NC} sip:${VPS_IP}:${SIP_PORT};transport=udp"
    echo ""
    echo -e "  ${BOLD}Next steps:${NC}"
    echo "  1. Configure your SIP provider to forward calls to: sip:${VPS_IP}:${SIP_PORT};transport=udp"
    echo "  2. Make sure your voice agent is running"
    echo "  3. Call your number to test!"
    echo ""
    echo -e "  ${BOLD}Useful commands:${NC}"
    echo "  sip-manage.sh status        — Check everything"
    echo "  sip-manage.sh test          — Run connectivity test"
    echo "  sip-manage.sh add-number    — Add another number"
    echo "  sip-manage.sh set-provider  — See provider setup guides"
    echo ""
}

# ============================================================
# Command: help
# ============================================================

cmd_help() {
    print_header "SIP Management Tool"

    echo ""
    echo -e "  ${BOLD}Usage:${NC} sip-manage.sh <command> [arguments]"
    echo ""
    echo -e "  ${BOLD}Commands:${NC}"
    echo ""
    echo -e "    ${CYAN}status${NC}                          Show all services and active numbers"
    echo -e "    ${CYAN}add-number${NC} +XXXXXXXXXXXX        Add a phone number"
    echo -e "    ${CYAN}remove-number${NC} +XXXXXXXXXXXX     Remove a phone number"
    echo -e "    ${CYAN}replace-number${NC} +OLD +NEW        Swap phone numbers (zero downtime)"
    echo -e "    ${CYAN}list-numbers${NC}                    List all active numbers"
    echo -e "    ${CYAN}set-provider${NC} [name]             Show provider setup instructions"
    echo -e "    ${CYAN}test${NC}                            Run full connectivity test"
    echo -e "    ${CYAN}restart${NC}                         Restart SIP container"
    echo -e "    ${CYAN}logs${NC} [lines|follow]             Show SIP logs (default: 20 lines)"
    echo -e "    ${CYAN}setup${NC}                           Interactive first-time setup wizard"
    echo -e "    ${CYAN}help${NC}                            Show this help"
    echo ""
    echo -e "  ${BOLD}Examples:${NC}"
    echo ""
    echo "    sip-manage.sh setup                                   # First-time setup"
    echo "    sip-manage.sh add-number +8801712345678               # Add BD number"
    echo "    sip-manage.sh replace-number +17745007904 +880171234  # Swap numbers"
    echo "    sip-manage.sh set-provider twilio                     # Twilio guide"
    echo "    sip-manage.sh set-provider hottelecom                 # HotTelecom guide"
    echo "    sip-manage.sh logs follow                             # Live log tail"
    echo ""
}

# ============================================================
# Main Router
# ============================================================

case "${1:-help}" in
    status)         cmd_status ;;
    add-number)     cmd_add_number "$2" ;;
    remove-number)  cmd_remove_number "$2" ;;
    replace-number) cmd_replace_number "$2" "$3" ;;
    list-numbers)   cmd_list_numbers ;;
    set-provider)   cmd_set_provider "$2" ;;
    test)           cmd_test ;;
    restart)        cmd_restart ;;
    logs)           cmd_logs "$2" ;;
    setup)          cmd_setup ;;
    help|--help|-h) cmd_help ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo "Run 'sip-manage.sh help' for usage."
        exit 1
        ;;
esac
