#!/bin/bash
# Activity 2: Evaluate student submission

EVAL_DIR="/home/.evaluationScripts"

# Make the directory itself traversable (but NOT recursive — that would reset evaluate.json perms)
chmod 755 /home/.evaluationScripts 2>/dev/null || true
chmod 755 /home/.evaluationScripts/activityInitiator 2>/dev/null || true

# evaluate.json is pre-baked in tarball — just ensure it's world-writable
chmod 666 "$EVAL_DIR/evaluate.json" 2>/dev/null || true

rm -f /tmp/submit_flag.txt /tmp/submit_hosts.txt /tmp/submit_count.txt

[ -f "/home/labDirectory/SUBMIT_FLAG.txt" ] && cp /home/labDirectory/SUBMIT_FLAG.txt /tmp/submit_flag.txt
[ -f "/home/labDirectory/SUBMIT_HOSTS.txt" ] && cp /home/labDirectory/SUBMIT_HOSTS.txt /tmp/submit_hosts.txt
[ -f "/home/labDirectory/SUBMIT_COUNT.txt" ] && cp /home/labDirectory/SUBMIT_COUNT.txt /tmp/submit_count.txt

# Run the autograder (writes to /tmp/evaluate.json)
python3 "$EVAL_DIR/autograder.py"

# Copy results to where the LMS expects them
cp /tmp/evaluate.json "$EVAL_DIR/evaluate.json" 2>/dev/null || true
