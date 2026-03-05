#!/bin/bash
# Activity 1: Guided DNS Zone Transfer Tutorial
# Do NOT use set -e

echo "[+] Initializing Activity 1 (Guided DNS Tutorial)..."

# ═══════════════════════════════════════════════════════════════════
# PART 1: INFRASTRUCTURE (Always do this first!)
# ═══════════════════════════════════════════════════════════════════

# evaluate.json is pre-baked in the tarball — just make it world-writable
# (No sudo touch needed; file already exists at mount time)
chmod 666 /home/.evaluationScripts/evaluate.json 2>/dev/null || true

# 3. Create writable submission files (NOT in tarball!)
sudo touch /home/labDirectory/SUBMIT_FLAG.txt
echo "(Paste the flag you found here)" | sudo tee /home/labDirectory/SUBMIT_FLAG.txt > /dev/null
sudo chmod 666 /home/labDirectory/SUBMIT_FLAG.txt
sudo chown student:student /home/labDirectory/SUBMIT_FLAG.txt

sudo touch /home/labDirectory/SUBMIT_ANSWER.txt
echo "(Type your answer here)" | sudo tee /home/labDirectory/SUBMIT_ANSWER.txt > /dev/null
sudo chmod 666 /home/labDirectory/SUBMIT_ANSWER.txt
sudo chown student:student /home/labDirectory/SUBMIT_ANSWER.txt

# ═══════════════════════════════════════════════════════════════════
# PART 2: BIND9 DNS SERVER SETUP
# ═══════════════════════════════════════════════════════════════════

# Write named.conf.options (allows zone transfer — THE VULNERABILITY)
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

# Write named.conf.local (zone declaration)
sudo tee /etc/bind/named.conf.local > /dev/null << 'NAMEDLOCAL'
zone "demo.lab.local" {
    type master;
    file "/etc/bind/db.demo.lab.local";
    allow-transfer { any; };
};
NAMEDLOCAL

# Copy zone file from evaluation scripts
if [ -f "/home/.evaluationScripts/activityInitiator/db.demo.lab.local" ]; then
    sudo cp /home/.evaluationScripts/activityInitiator/db.demo.lab.local /etc/bind/db.demo.lab.local
    sudo chown bind:bind /etc/bind/db.demo.lab.local
    sudo chmod 644 /etc/bind/db.demo.lab.local
    echo "[+] Zone file installed"
else
    echo "[!] Warning: Zone file not found"
fi

# Start BIND9
echo "[+] Starting DNS server..."
sudo service named start 2>/dev/null || sudo named -g &
sleep 2

# Verify DNS is running
if dig @127.0.0.1 demo.lab.local SOA +short > /dev/null 2>&1; then
    echo "[+] DNS server running successfully"
else
    echo "[!] Warning: DNS server may not be responding"
    # Try alternative start method
    sudo named -c /etc/bind/named.conf &
    sleep 2
fi

# ═══════════════════════════════════════════════════════════════════
# PART 3: CLEANUP & LOCKDOWN
# ═══════════════════════════════════════════════════════════════════

# Ensure student owns labDirectory files
sudo chown -R student:student /home/labDirectory

# Revoke temporary sudo access
echo "[*] Revoking sudo privileges..."
if [ -f "/etc/sudoers.d/student_temp" ]; then
    sudo rm -f /etc/sudoers.d/student_temp
    echo "[+] Sudo access revoked"
else
    echo "[!] Warning: sudoers file not found"
fi

echo "[+] Activity 1 initialization complete!"
echo "[+] A DNS server is running on localhost. Read README.md to get started."
