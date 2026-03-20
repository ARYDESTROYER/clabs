#!/bin/bash
# Do not use set -e. We want the lab to finish infrastructure setup even if
# a non-critical step fails.

echo "[+] Initializing Crypto Activity..."

# --- PART 1: INFRASTRUCTURE & PERMISSIONS (Critical) ---

LAB_DIR="/home/labDirectory"
EVAL_DIR="/home/.evaluationScripts"
SUBMISSION_FILE_PLURAL="$LAB_DIR/SUBMIT_FLAGS_HERE.txt"
SUBMISSION_FILE_SINGULAR="$LAB_DIR/SUBMIT_FLAG_HERE.txt"

# Ensure student owns the working directory before we create writable files.
sudo chown -R student:student "$LAB_DIR"
sudo chmod 777 "$LAB_DIR"

# Keep the evaluation directory traversable but do not chmod it recursively.
sudo chmod 755 "$EVAL_DIR" "$EVAL_DIR/activityInitiator" 2>/dev/null || true
sudo chmod 755 "$EVAL_DIR/evaluate.sh" "$EVAL_DIR/autograder.py" "$EVAL_DIR/activityInitiator/initactivity.sh" 2>/dev/null || true

# Create writable student submission templates at runtime.
# Keep both names for LMS/editor compatibility across activities.
cat > "$SUBMISSION_FILE_PLURAL" <<'EOF'
Submit your fragments in this file.
Enter only the fragment value after each label.
The final decoded flag should be of the form IITB{decoded_message}.

Fragment 1:
Fragment 2:
Fragment 3:
Fragment 4 (Password):
Fragment 5:
Fragment 6:
Final Decoded Flag:
EOF
rm -f "$SUBMISSION_FILE_SINGULAR"
ln "$SUBMISSION_FILE_PLURAL" "$SUBMISSION_FILE_SINGULAR" 2>/dev/null || cp "$SUBMISSION_FILE_PLURAL" "$SUBMISSION_FILE_SINGULAR"

# Force broad readability/writability as requested.
chmod 666 "$SUBMISSION_FILE_PLURAL" "$SUBMISSION_FILE_SINGULAR"
chmod a+rwX "$LAB_DIR" 2>/dev/null || true

# Revoke temporary sudo access after initialization.
sudo rm -f /etc/sudoers.d/student_temp

echo "[+] Initialization complete."
