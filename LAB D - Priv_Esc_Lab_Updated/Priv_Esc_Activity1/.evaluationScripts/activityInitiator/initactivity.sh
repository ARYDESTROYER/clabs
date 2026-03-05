#!/bin/bash
# Remove set -e to prevent the script from aborting on minor errors.
# We will handle critical errors manually.
# set -e

echo "[+] Initializing Activity 1 (SUID Enumeration)..."

# --- PART 1: INFRASTRUCTURE & PERMISSIONS (Critical) ---

# 1. Setup Evaluation Permissions (Fixes the Autograder PermissionError)
# Pre-create evaluate.json and set permissions so student/autograder can write to it
sudo touch /home/.evaluationScripts/evaluate.json
sudo chown student:student /home/.evaluationScripts/evaluate.json
sudo chmod 666 /home/.evaluationScripts/evaluate.json

# Ensure the .evaluationScripts folder is traverseable/readable
sudo chmod -R 777 /home/.evaluationScripts || true

# FIX: Ensure the student owns the mount point itself
sudo chown -R student:student /home/labDirectory

# 2. Setup Student Submission File
# CRITICAL: This file is NOT in the tarball, so LMS won't mark it as read-only.
# We create it fresh at runtime so students can write to it.
echo "[*] Creating SUBMIT_SUID_NAMES.txt (fresh, not from tarball)..."
sudo touch /home/labDirectory/SUBMIT_SUID_NAMES.txt
echo "(Write the names of the 3 suspected SUID binaries here, one per line)" | sudo tee /home/labDirectory/SUBMIT_SUID_NAMES.txt > /dev/null
sudo chmod 666 /home/labDirectory/SUBMIT_SUID_NAMES.txt
sudo chown student:student /home/labDirectory/SUBMIT_SUID_NAMES.txt
echo "[+] SUBMIT_SUID_NAMES.txt created and is writable."

# --- PART 2: VULNERABLE ENVIRONMENT (Task) ---

# 3. Compile SUID binaries
echo "[*] Compiling binaries..."

for bin in sysmonitor logrotate_s envcheck; do
    if [ -f "/home/.evaluationScripts/activityInitiator/$bin.c" ]; then
        sudo gcc "/home/.evaluationScripts/activityInitiator/$bin.c" -o "/usr/local/bin/$bin"
        sudo chown root:root "/usr/local/bin/$bin"
        sudo chmod 4755 "/usr/local/bin/$bin"
        echo "[+] $bin compiled and SUID set."
    else
        echo "[!] Warning: $bin.c not found, skipping."
    fi
done

# Set SUID on 'passwd' (Standard requirement)
sudo chmod u+s /usr/bin/passwd 2>/dev/null || true

# 4. Place linpeas
if [ -f "/home/.evaluationScripts/linpeas.sh" ]; then
    cp /home/.evaluationScripts/linpeas.sh /home/labDirectory/linpeas.sh
    chown student:student /home/labDirectory/linpeas.sh
    chmod +x /home/labDirectory/linpeas.sh
    echo "[+] linpeas.sh placed in labDirectory."
else
    echo "[!] Warning: linpeas.sh not found."
fi

# Fix permissions recursively for student directory
echo "[*] Ensuring student ownership of /home/labDirectory..."
sudo chown -R student:student /home/labDirectory

# --- PART 3: CLEANUP ---

# 5. Revoke Sudo (Lockdown)
echo "[*] Locking down..."
if [ -f "/etc/sudoers.d/student_temp" ]; then
    sudo rm -f /etc/sudoers.d/student_temp
    echo "[+] Sudo revoked."
else
    echo "[!] Warning: Sudo config file not found (already locked?)"
fi

echo "[+] Activity 1 Initialization Complete."