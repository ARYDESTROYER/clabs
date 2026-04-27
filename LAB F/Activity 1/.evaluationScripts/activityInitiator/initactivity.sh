#!/bin/bash
# LAB F Activity 1 -- threat model & enumeration.
# Follows the multi-service init template in Section 4.6.9 of the BodhiLabs guide.
# Do NOT use `set -e`.

LAB_DIR="/home/labDirectory"
EVAL_DIR="/home/.evaluationScripts"
INIT_DIR="$EVAL_DIR/activityInitiator"
RUNTIME_DIR="/opt/labf"
ACTIVITY_ID="1"
INIT_LOG="/tmp/labf_init.log"

echo "[$(date)] LAB F Activity 1 init start" > "$INIT_LOG"
echo "[$(date)] user=$(id -un 2>/dev/null), python=$(command -v python3)" >> "$INIT_LOG"

# === PART 1: INFRASTRUCTURE & PERMISSIONS (Section 7.7 / 7.1 / 7.8) ===
sudo chmod 755 "$EVAL_DIR" "$INIT_DIR" 2>/dev/null || true
sudo chmod 666 "$EVAL_DIR/evaluate.json" 2>/dev/null || true
sudo chown -R student:student "$LAB_DIR" 2>/dev/null || true

# Submission file -- recreated every boot so the LMS editor can save it.
for f in flag.txt; do
    sudo rm -f "$LAB_DIR/$f" 2>/dev/null || true
    : | sudo tee "$LAB_DIR/$f" > /dev/null
    sudo chown student:student "$LAB_DIR/$f" 2>/dev/null || true
    sudo chmod 666 "$LAB_DIR/$f" 2>/dev/null || true
done

# === PART 2: STAGE RUNTIME CODE ===
sudo mkdir -p "$RUNTIME_DIR"
sudo chown -R student:student "$RUNTIME_DIR" 2>/dev/null || true
cp "$INIT_DIR/attacker_server.py" "$RUNTIME_DIR/attacker_server.py"
cp "$INIT_DIR/admin_server.py"    "$RUNTIME_DIR/admin_server.py"
chmod +x "$RUNTIME_DIR/attacker_server.py" "$RUNTIME_DIR/admin_server.py" 2>/dev/null || true

# Activity 1 ships harmless placeholder configs so the dashboard renders.
cat > "$LAB_DIR/dns_config.json" <<'JSON'
{
  "_comment": "Activity 1 does not require running the bot. These placeholders just keep the dashboard happy.",
  "hostnames": [
    { "hostname": "attacker.lab", "initial_ip": "127.0.0.1", "initial_port": 30000 }
  ]
}
JSON
cat > "$LAB_DIR/attack_plan.json" <<'JSON'
{
  "_comment": "Activity 1: nothing to do here. Move on to Activity 2.",
  "page_url": "http://attacker.lab/payload",
  "victim_actions": []
}
JSON
chown student:student "$LAB_DIR/dns_config.json" "$LAB_DIR/attack_plan.json" 2>/dev/null || true
chmod 666 "$LAB_DIR/dns_config.json" "$LAB_DIR/attack_plan.json" 2>/dev/null || true

# === PART 3: KILL OLD INSTANCES (Section 4.6.6 idempotency) ===
pkill -f admin_server.py    2>/dev/null || true
pkill -f attacker_server.py 2>/dev/null || true
sleep 1

# === PART 4: LAUNCH SERVICES (Section 4.6.2 launch primitive) ===
echo "[$(date)] launching admin_server (127.0.0.1:8080)" >> "$INIT_LOG"
nohup python3 "$RUNTIME_DIR/admin_server.py" >/tmp/labf_admin.log 2>&1 &
disown 2>/dev/null || true
sleep 2

echo "[$(date)] launching attacker_server (0.0.0.0:30000)" >> "$INIT_LOG"
ACTIVITY_ID="$ACTIVITY_ID" nohup python3 "$RUNTIME_DIR/attacker_server.py" >/tmp/labf_attacker.log 2>&1 &
disown 2>/dev/null || true

# === PART 5: VERIFY (Section 4.6.7) ===
for i in $(seq 1 20); do
    listen=$(ss -ltn 2>/dev/null | grep -E ':(30000|8080)\b' || \
             netstat -ltn 2>/dev/null | grep -E ':(30000|8080)\b')
    if [ -n "$listen" ] && \
       echo "$listen" | grep -q ':30000' && \
       echo "$listen" | grep -q ':8080'; then
        break
    fi
    sleep 0.5
done
echo "[$(date)] services up:" >> "$INIT_LOG"
ss -ltn 2>/dev/null | grep -E ':(30000|8080)' >> "$INIT_LOG" || \
    netstat -ltn 2>/dev/null | grep -E ':(30000|8080)' >> "$INIT_LOG" || true
{ echo "--- admin log ---"; tail -20 /tmp/labf_admin.log 2>/dev/null;
  echo "--- attacker log ---"; tail -20 /tmp/labf_attacker.log 2>/dev/null; } >> "$INIT_LOG"

# === PART 6: LOCKDOWN (Section 7.3) ===
if [ -f /etc/sudoers.d/student_temp ]; then
    sudo rm -f /etc/sudoers.d/student_temp
fi
echo "[$(date)] init complete" >> "$INIT_LOG"

exit 0
