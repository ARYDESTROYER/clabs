#!/bin/bash
# Activity 1: Evaluate student submission

EVAL_DIR="/home/.evaluationScripts"

# Make the directory itself traversable (but NOT recursive — that would reset evaluate.json perms)
chmod 755 /home/.evaluationScripts 2>/dev/null || true
chmod 755 /home/.evaluationScripts/activityInitiator 2>/dev/null || true

# evaluate.json is pre-baked in tarball — just ensure it's world-writable
chmod 666 "$EVAL_DIR/evaluate.json" 2>/dev/null || true

# Clean up previous temp files
rm -f /tmp/submit_flag.txt /tmp/submit_answer.txt

# Copy student submissions to /tmp (avoids permission issues with read-only mounts)
[ -f "/home/labDirectory/SUBMIT_FLAG.txt" ] && cp /home/labDirectory/SUBMIT_FLAG.txt /tmp/submit_flag.txt
[ -f "/home/labDirectory/SUBMIT_ANSWER.txt" ] && cp /home/labDirectory/SUBMIT_ANSWER.txt /tmp/submit_answer.txt

# Run the autograder (writes to /tmp/evaluate.json)
python3 "$EVAL_DIR/autograder.py"

# Copy results to where the LMS expects them
cp /tmp/evaluate.json "$EVAL_DIR/evaluate.json" 2>/dev/null || true
