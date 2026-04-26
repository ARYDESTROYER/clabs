#!/bin/bash
# LAB B1 Activity 3 - BookHaven (independent audit).
# Apache + mod_security in front of the BookHaven Flask app, same misconfig
# pattern as Activity 2 but the student is not given a walkthrough.

LAB_DIR="/home/labDirectory"
EVAL_DIR="/home/.evaluationScripts"
INIT_DIR="$EVAL_DIR/activityInitiator"
APP_DIR="/opt/bookhaven"
INIT_LOG="/tmp/labb1_init.log"

echo "[$(date)] LAB B1 Activity 3 init start" > "$INIT_LOG"

# === PART 1: INFRASTRUCTURE & PERMISSIONS ===
sudo chmod 755 "$EVAL_DIR" "$INIT_DIR" 2>/dev/null || true
sudo chmod 666 "$EVAL_DIR/evaluate.json" 2>/dev/null || true
sudo chown -R student:student "$LAB_DIR" 2>/dev/null || true

for f in flag1.txt flag2.txt; do
    rm -f "$LAB_DIR/$f" 2>/dev/null || true
    : > "$LAB_DIR/$f"
    sudo chown student:student "$LAB_DIR/$f" 2>/dev/null || true
    sudo chmod 666 "$LAB_DIR/$f" 2>/dev/null || true
done

# === PART 2: DEPLOY THE FLASK APP ===
sudo mkdir -p "$APP_DIR"
sudo cp "$INIT_DIR/bookhaven.py" "$APP_DIR/bookhaven.py"
sudo chmod 755 "$APP_DIR/bookhaven.py"

# === PART 3: APACHE + MOD_SECURITY CONFIG ===
echo "Listen 30000" | sudo tee /etc/apache2/ports.conf >/dev/null

sudo a2enmod security2 rewrite proxy proxy_http headers >/dev/null 2>&1 || true
sudo a2dissite 000-default >/dev/null 2>&1 || true

sudo cp "$INIT_DIR/apache_site.conf" /etc/apache2/sites-available/bookhaven.conf
sudo a2ensite bookhaven.conf >/dev/null 2>&1 || true

if [ -f /etc/modsecurity/modsecurity.conf-recommended ]; then
    sudo cp /etc/modsecurity/modsecurity.conf-recommended /etc/modsecurity/modsecurity.conf
fi
sudo sed -i 's|^SecRuleEngine .*|SecRuleEngine On|' /etc/modsecurity/modsecurity.conf 2>/dev/null || true
sudo sed -i 's|^SecAuditLog .*|SecAuditLog /tmp/modsec_audit.log|' /etc/modsecurity/modsecurity.conf 2>/dev/null || true
sudo sed -i 's|^SecAuditLogType .*|SecAuditLogType Serial|' /etc/modsecurity/modsecurity.conf 2>/dev/null || true

sudo touch /tmp/modsec_audit.log
sudo chmod 666 /tmp/modsec_audit.log

sudo cp "$INIT_DIR/modsec_rules.conf" /etc/modsecurity/lab_rules.conf

# === PART 4: START SERVICES ===
sudo apache2ctl stop 2>/dev/null || true
pkill -f bookhaven.py 2>/dev/null || true
sleep 1

nohup python3 "$APP_DIR/bookhaven.py" >/tmp/bookhaven.log 2>&1 &
disown 2>/dev/null || true
sleep 2

# Stop any leftover juicymart from a previous activity (defensive, not strictly needed).
pkill -f juicymart.py 2>/dev/null || true

sudo apache2ctl start >>"$INIT_LOG" 2>&1 || sudo service apache2 start >>"$INIT_LOG" 2>&1 || true

sleep 2
echo "[$(date)] services up:" >> "$INIT_LOG"
ss -ltn 2>/dev/null | grep -E '5000|30000' >> "$INIT_LOG" || \
    netstat -ltn 2>/dev/null | grep -E '5000|30000' >> "$INIT_LOG" || true

# === PART 5: LOCKDOWN ===
sudo rm -f /etc/sudoers.d/student_temp
echo "[$(date)] init complete" >> "$INIT_LOG"
exit 0
