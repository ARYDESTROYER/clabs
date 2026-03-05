#!/bin/bash
set -e
echo "[+] Initializing Activity 1 environment..."
# -------------------------
# Root-only setup via sudo
# -------------------------
# Compile SUID binaries
sudo gcc /home/.evaluationScripts/activityInitiator/sysmonitor.c \
    -o /usr/local/bin/sysmonitor
sudo gcc /home/.evaluationScripts/activityInitiator/logrotate_s.c \
    -o /usr/local/bin/logrotate_s
sudo gcc /home/.evaluationScripts/activityInitiator/envcheck.c \
    -o /usr/local/bin/envcheck
# Set ownership and SUID bit
sudo chown root:root \
    /usr/local/bin/sysmonitor \
    /usr/local/bin/logrotate_s \
    /usr/local/bin/envcheck
sudo chmod 4755 \
    /usr/local/bin/sysmonitor \
    /usr/local/bin/logrotate_s \
    /usr/local/bin/envcheck
# Place linpeas
sudo cp /home/.evaluationScripts/linpeas.sh /usr/local/bin/linpeas
sudo chmod 755 /usr/local/bin/linpeas
# -------------------------
# CRITICAL: Revoke sudo
# -------------------------
chmod 700 /root
sudo rm -f /etc/sudoers.d/student_temp
echo "[+] Initialization complete."
echo "[+] Student privileges locked."
exec su - student