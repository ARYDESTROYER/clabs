#!/bin/bash
# Remove set -e to prevent the script from aborting on minor errors.
# We will handle critical errors manually.
# set -e 

echo "[+] Initializing Activity 3 (GTFOBins Exploitation)..."

# --- PART 1: INFRASTRUCTURE & PERMISSIONS (Critical) ---

# 1. Setup Evaluation Permissions (Fixes the Autograder PermissionError)
# Pre-create evaluate.json and set permissions so student/autograder can write to it
sudo touch /home/.evaluationScripts/evaluate.json
sudo chown student:student /home/.evaluationScripts/evaluate.json
sudo chmod 666 /home/.evaluationScripts/evaluate.json

# Ensure the .evaluationScripts folder is traverseable/readable
sudo chmod -R 777 /home/.evaluationScripts || true

# 2. Setup Student Submission File
# CRITICAL: This file is NOT in the tarball, so LMS won't mark it as read-only.
# We create it fresh at runtime so students can write to it.
echo "[*] Creating SUBMIT_FLAG_HERE.txt (fresh, not from tarball)..."
sudo touch /home/labDirectory/SUBMIT_FLAG_HERE.txt
echo "(Paste your flag here)" | sudo tee /home/labDirectory/SUBMIT_FLAG_HERE.txt > /dev/null
sudo chmod 666 /home/labDirectory/SUBMIT_FLAG_HERE.txt
sudo chown student:student /home/labDirectory/SUBMIT_FLAG_HERE.txt
echo "[+] SUBMIT_FLAG_HERE.txt created and is writable."

# 3. Create the Root Flag
echo "IITB{gtf0_b1ns_su1d_m4st3r}" | sudo tee /root/flag.txt > /dev/null
sudo chmod 400 /root/flag.txt
echo "[+] Flag created at /root/flag.txt"

# --- PART 2: VULNERABLE ENVIRONMENT (Task) ---

echo "[*] Configuring SUID binaries..."

# 4. Set SUID on vim (The Primary Target)
# Ubuntu often uses /usr/bin/vim.basic as the real binary
if [ -f "/usr/bin/vim.basic" ]; then
    sudo chmod u+s /usr/bin/vim.basic
    echo "[+] SUID set on vim.basic"
else 
    # Fallback to standard vim path if .basic doesn't exist
    if [ -f "/usr/bin/vim" ]; then
        sudo chmod u+s /usr/bin/vim
        echo "[+] SUID set on vim"
    else
        echo "[!] WARNING: vim not found!"
    fi
fi

# 5. Set SUID on Distractors (less, awk)
# These are present on the base image
if [ -f "/usr/bin/less" ]; then
    sudo chmod u+s /usr/bin/less
    echo "[+] SUID set on less"
fi

if [ -f "/usr/bin/awk" ]; then
    sudo chmod u+s /usr/bin/awk
    echo "[+] SUID set on awk"
fi

# Set SUID on 'passwd' (Standard requirement)
sudo chmod u+s /usr/bin/passwd 2>/dev/null || true

# 6. Place linpeas
if [ -f "/home/.evaluationScripts/linpeas.sh" ]; then
    cp /home/.evaluationScripts/linpeas.sh /home/labDirectory/linpeas.sh
    # Set permissions: Owner student, Executable
    chown student:student /home/labDirectory/linpeas.sh
    chmod +x /home/labDirectory/linpeas.sh
else
    echo "[!] Warning: linpeas.sh not found."
fi

# Fix permissions recursively for student directory
# (Critical: ensures student can create files like rootshell.c)
echo "[*] Ensuring student ownership of /home/labDirectory..."
sudo chown -R student:student /home/labDirectory

# --- PART 3: CLEANUP ---

# 7. Revoke Sudo (Lockdown)
echo "[*] Locking down..."
if [ -f "/etc/sudoers.d/student_temp" ]; then
    sudo rm -f /etc/sudoers.d/student_temp
    echo "[+] Sudo revoked."
else
    echo "[!] Warning: Sudo config file not found (already locked?)"
fi

echo "[+] Activity 3 Initialization Complete."
