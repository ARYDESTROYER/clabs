#!/bin/bash
# LAB B1 Activity 1 - JuicyMart Recon
# Sets up Apache + mod_security in front of a Flask app, opens the audit log
# to the student, creates the submission file, then revokes sudo.

LAB_DIR="/home/labDirectory"
EVAL_DIR="/home/.evaluationScripts"
INIT_DIR="$EVAL_DIR/activityInitiator"
APP_DIR="/opt/juicymart"
INIT_LOG="/tmp/labb1_init.log"

echo "[$(date)] LAB B1 Activity 1 init start" > "$INIT_LOG"

# === PART 1: INFRASTRUCTURE & PERMISSIONS ===
sudo chmod 755 "$EVAL_DIR" "$INIT_DIR" 2>/dev/null || true
sudo chmod 666 "$EVAL_DIR/evaluate.json" 2>/dev/null || true
sudo chown -R student:student "$LAB_DIR" 2>/dev/null || true

# Submission file: created at runtime so the LMS doesn't mark it read-only.
rm -f "$LAB_DIR/flag.txt" 2>/dev/null || true
: > "$LAB_DIR/flag.txt"
sudo chown student:student "$LAB_DIR/flag.txt" 2>/dev/null || true
sudo chmod 666 "$LAB_DIR/flag.txt" 2>/dev/null || true

# === PART 2: DEPLOY THE FLASK APP ===
sudo mkdir -p "$APP_DIR"
sudo cp "$INIT_DIR/juicymart.py" "$APP_DIR/juicymart.py"
sudo chmod 755 "$APP_DIR/juicymart.py"

# === PART 3: APACHE + MOD_SECURITY CONFIG ===
# Listen on the LMS-exposed port instead of 80.
echo "Listen 30000" | sudo tee /etc/apache2/ports.conf >/dev/null

# Enable required modules.
sudo a2enmod security2 rewrite proxy proxy_http headers >/dev/null 2>&1 || true
sudo a2dissite 000-default >/dev/null 2>&1 || true

# Install our vhost.
sudo cp "$INIT_DIR/apache_site.conf" /etc/apache2/sites-available/juicymart.conf
sudo a2ensite juicymart.conf >/dev/null 2>&1 || true

# mod_security base config: copy recommended, flip to On, route audit log to /tmp.
if [ -f /etc/modsecurity/modsecurity.conf-recommended ]; then
    sudo cp /etc/modsecurity/modsecurity.conf-recommended /etc/modsecurity/modsecurity.conf
fi
sudo sed -i 's|^SecRuleEngine .*|SecRuleEngine On|' /etc/modsecurity/modsecurity.conf 2>/dev/null || true
sudo sed -i 's|^SecAuditLog .*|SecAuditLog /tmp/modsec_audit.log|' /etc/modsecurity/modsecurity.conf 2>/dev/null || true
sudo sed -i 's|^SecAuditLogType .*|SecAuditLogType Serial|' /etc/modsecurity/modsecurity.conf 2>/dev/null || true

# Pre-create the audit log file as world-read/write so the Flask app and the
# student can both read it, and Apache (running as www-data) can write to it.
sudo touch /tmp/modsec_audit.log
sudo chmod 666 /tmp/modsec_audit.log

# Drop our custom rules into the modsecurity config dir. The existing
# /etc/apache2/mods-enabled/security2.conf already does
# `IncludeOptional /etc/modsecurity/*.conf`, so this single file is enough.
# DO NOT also include via /etc/apache2/conf-available, or rules load twice.
sudo cp "$INIT_DIR/modsec_rules.conf" /etc/modsecurity/lab_rules.conf

# === PART 4: START SERVICES ===
# Stop anything that may already be running so init is idempotent.
sudo apache2ctl stop 2>/dev/null || true
pkill -f juicymart.py 2>/dev/null || true
sleep 1

# Start Flask app as student in the background, output to /tmp so we don't
# need write access to /var/log.
nohup python3 "$APP_DIR/juicymart.py" >/tmp/juicymart.log 2>&1 &
disown 2>/dev/null || true
sleep 2

# Start Apache. apache2ctl daemonizes; the LMS keeps the container alive
# via the CMD's sleep loop.
sudo apache2ctl start >>"$INIT_LOG" 2>&1 || sudo service apache2 start >>"$INIT_LOG" 2>&1 || true

sleep 2
echo "[$(date)] services up:" >> "$INIT_LOG"
ss -ltn 2>/dev/null | grep -E '5000|30000' >> "$INIT_LOG" || \
    netstat -ltn 2>/dev/null | grep -E '5000|30000' >> "$INIT_LOG" || true

# === PART 5: LOCKDOWN ===
# Revoke temporary sudo so students can't tamper with the WAF or app.
sudo rm -f /etc/sudoers.d/student_temp
echo "[$(date)] init complete" >> "$INIT_LOG"
exit 0
