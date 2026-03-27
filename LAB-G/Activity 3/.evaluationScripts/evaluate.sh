#!/bin/bash
set -euo pipefail

EVAL_DIR="/home/.evaluationScripts"

chmod 755 /home/.evaluationScripts 2>/dev/null || true
chmod 755 /home/.evaluationScripts/activityInitiator 2>/dev/null || true
chmod 666 "$EVAL_DIR/evaluate.json" 2>/dev/null || true

for f in xss-payload.txt flag.txt; do
  rm -f "/tmp/$f"
  if [ -f "/home/labDirectory/$f" ]; then
    cp "/home/labDirectory/$f" "/tmp/$f"
    chmod 644 "/tmp/$f"
  fi
done

python3 "$EVAL_DIR/autograder.py"
cp /tmp/evaluate.json "$EVAL_DIR/evaluate.json" 2>/dev/null || true
