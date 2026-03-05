#!/bin/bash
# Activity 2: Intermediate DNS Zone Transfer Challenge
# Do NOT use set -e

echo "[+] Initializing Activity 2 (Intermediate AXFR Challenge)..."

# ═══════════════════════════════════════════════════════════════════
# PART 1: INFRASTRUCTURE
# ═══════════════════════════════════════════════════════════════════

# evaluate.json is pre-baked in the tarball — just make it world-writable
# (No sudo touch needed; file already exists at mount time)
chmod 666 /home/.evaluationScripts/evaluate.json 2>/dev/null || true

# Create writable submission files at runtime
for f in SUBMIT_FLAG.txt SUBMIT_HOSTS.txt SUBMIT_COUNT.txt; do
    sudo touch "/home/labDirectory/$f"
    echo "(Write your answer here)" | sudo tee "/home/labDirectory/$f" > /dev/null
    sudo chmod 666 "/home/labDirectory/$f"
    sudo chown student:student "/home/labDirectory/$f"
done

# ═══════════════════════════════════════════════════════════════════
# PART 2: BIND9 DNS SERVER SETUP
# ═══════════════════════════════════════════════════════════════════

# named.conf.options (allows zone transfer — THE VULNERABILITY)
sudo tee /etc/bind/named.conf.options > /dev/null << 'NAMEDOPTS'
options {
    directory "/var/cache/bind";
    recursion no;
    listen-on { 127.0.0.1; };
    listen-on-v6 { none; };
    allow-query { any; };
    allow-transfer { any; };
};
NAMEDOPTS

# named.conf.local (zone declaration)
sudo tee /etc/bind/named.conf.local > /dev/null << 'NAMEDLOCAL'
zone "corp.internal" {
    type master;
    file "/etc/bind/db.corp.internal";
    allow-transfer { any; };
};
NAMEDLOCAL

# Copy zone file
if [ -f "/home/.evaluationScripts/activityInitiator/db.corp.internal" ]; then
    sudo cp /home/.evaluationScripts/activityInitiator/db.corp.internal /etc/bind/db.corp.internal
    sudo chown bind:bind /etc/bind/db.corp.internal
    sudo chmod 644 /etc/bind/db.corp.internal
    echo "[+] Zone file installed"
else
    echo "[!] Warning: Zone file not found"
fi

# Start BIND9
echo "[+] Starting DNS server..."
sudo service named start 2>/dev/null || sudo named -g &
sleep 2

if dig @127.0.0.1 corp.internal SOA +short > /dev/null 2>&1; then
    echo "[+] DNS server running successfully"
else
    echo "[!] Warning: DNS server may not be responding"
    sudo named -c /etc/bind/named.conf &
    sleep 2
fi

# ═══════════════════════════════════════════════════════════════════
# PART 3: CLEANUP & LOCKDOWN
# ═══════════════════════════════════════════════════════════════════

sudo chown -R student:student /home/labDirectory

echo "[*] Revoking sudo privileges..."
if [ -f "/etc/sudoers.d/student_temp" ]; then
    sudo rm -f /etc/sudoers.d/student_temp
    echo "[+] Sudo access revoked"
fi

echo "[+] Activity 2 initialization complete!"
