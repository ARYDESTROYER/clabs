#!/bin/bash
# Remove set -e to prevent the script from aborting on minor errors.
# We will handle critical errors manually.
# set -e 

echo "[+] Initializing Activity 2 (PATH Exploit)..."

# --- PART 1: INFRASTRUCTURE & PERMISSIONS (Critical) ---

# FIX: Ensure the student owns the mount point itself
sudo chown -R student:student /home/labDirectory

# 1. Setup Evaluation Permissions (Fixes the Autograder PermissionError)
# Pre-create evaluate.json and set permissions so student/autograder can write to it
sudo touch /home/.evaluationScripts/evaluate.json
sudo chown student:student /home/.evaluationScripts/evaluate.json
sudo chmod 666 /home/.evaluationScripts/evaluate.json

# Ensure the .evaluationScripts folder is traverseable/readable
sudo chmod -R 777 /home/.evaluationScripts || true

# 2. Setup Student Submission File
# Ensure the submission file exists and is writable by the student
sudo touch /home/labDirectory/SUBMIT_FLAG_HERE.txt
sudo chmod 777 /home/labDirectory/SUBMIT_FLAG_HERE.txt
sudo chown student:student /home/labDirectory/SUBMIT_FLAG_HERE.txt

# 3. Create the Root Flag
echo "IITB{p4th_v4r_m4n1pul4t10n_succ3ss}" | sudo tee /root/flag.txt > /dev/null
sudo chmod 400 /root/flag.txt
echo "[+] Flag created at /root/flag.txt"

# --- PART 2: VULNERABLE ENVIRONMENT (Task) ---

# 4. Setup dummy file for sysbackup
sudo touch /var/log/syslog.bak
sudo chmod 666 /var/log/syslog.bak

# 5. Compile Binaries
echo "[*] Compiling binaries..."

# Compile sysbackup (Critical Vulnerability)
if [ -f "/home/.evaluationScripts/activityInitiator/sysbackup.c" ]; then
    sudo gcc /home/.evaluationScripts/activityInitiator/sysbackup.c -o /usr/local/bin/sysbackup
    sudo chown root:root /usr/local/bin/sysbackup
    sudo chmod 4755 /usr/local/bin/sysbackup
    echo "[+] sysbackup compiled and SUID set."
else
    echo "[!] ERROR: sysbackup.c not found."
fi

# Compile Decoys (envcheck, etc.)
for bin in envcheck logrotate_s sysmonitor; do
    if [ -f "/home/.evaluationScripts/activityInitiator/$bin.c" ]; then
        sudo gcc "/home/.evaluationScripts/activityInitiator/$bin.c" -o "/usr/local/bin/$bin"
        sudo chown root:root "/usr/local/bin/$bin"
        sudo chmod 4755 "/usr/local/bin/$bin"
    else
        echo "[!] Warning: $bin.c not found, skipping."
    fi
done

# Set SUID on 'passwd'
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

# --- PART 3: CLEANUP ---

# 7. Revoke Sudo (Lockdown)
echo "[*] Locking down..."
if [ -f "/etc/sudoers.d/student_temp" ]; then
    sudo rm -f /etc/sudoers.d/student_temp
    echo "[+] Sudo revoked."
else
    echo "[!] Warning: Sudo config file not found (already locked?)"
fi

echo "[+] Activity 2 Initialization Complete."
