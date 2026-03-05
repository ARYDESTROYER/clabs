#!/bin/bash
# Activity 3: Advanced DNS Tunneling Detection
# Do NOT use set -e

echo "[+] Initializing Activity 3 (DNS Tunneling Detection)..."

# ═══════════════════════════════════════════════════════════════════
# PART 1: INFRASTRUCTURE
# ═══════════════════════════════════════════════════════════════════

# evaluate.json is pre-baked in the tarball — just make it world-writable
# (No sudo touch needed; file already exists at mount time)
chmod 666 /home/.evaluationScripts/evaluate.json 2>/dev/null || true

# Create writable submission files at runtime
for f in SUBMIT_DOMAIN.txt SUBMIT_SECRET.txt SUBMIT_TUNNEL_COUNT.txt; do
    sudo touch "/home/labDirectory/$f"
    echo "(Write your answer here)" | sudo tee "/home/labDirectory/$f" > /dev/null
    sudo chmod 666 "/home/labDirectory/$f"
    sudo chown student:student "/home/labDirectory/$f"
done

# ═══════════════════════════════════════════════════════════════════
# PART 2: ENSURE PCAP IS ACCESSIBLE
# ═══════════════════════════════════════════════════════════════════

# The pcap is pre-baked in the student_directory tarball
if [ -f "/home/labDirectory/dns_traffic.pcap" ]; then
    sudo chmod 644 /home/labDirectory/dns_traffic.pcap
    echo "[+] Pcap file found and accessible"
else
    echo "[!] Warning: dns_traffic.pcap not found in labDirectory"
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

echo "[+] Activity 3 initialization complete!"
