#!/bin/bash
# Activity 3: Evaluate student submission

EVAL_DIR="/home/.evaluationScripts"

# Make the directory itself traversable (but NOT recursive — that would reset evaluate.json perms)
chmod 755 /home/.evaluationScripts 2>/dev/null || true
chmod 755 /home/.evaluationScripts/activityInitiator 2>/dev/null || true

# evaluate.json is pre-baked in tarball — just ensure it's world-writable
chmod 666 "$EVAL_DIR/evaluate.json" 2>/dev/null || true

rm -f /tmp/submit_domain.txt /tmp/submit_secret.txt /tmp/submit_tunnel_count.txt

[ -f "/home/labDirectory/SUBMIT_DOMAIN.txt" ] && cp /home/labDirectory/SUBMIT_DOMAIN.txt /tmp/submit_domain.txt
[ -f "/home/labDirectory/SUBMIT_SECRET.txt" ] && cp /home/labDirectory/SUBMIT_SECRET.txt /tmp/submit_secret.txt
[ -f "/home/labDirectory/SUBMIT_TUNNEL_COUNT.txt" ] && cp /home/labDirectory/SUBMIT_TUNNEL_COUNT.txt /tmp/submit_tunnel_count.txt

# Run the autograder (writes to /tmp/evaluate.json)
python3 "$EVAL_DIR/autograder.py"

# Copy results to where the LMS expects them
cp /tmp/evaluate.json "$EVAL_DIR/evaluate.json" 2>/dev/null || true
