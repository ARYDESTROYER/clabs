#!/bin/bash
set -euo pipefail

EVAL_DIR="/home/.evaluationScripts"

chmod 755 /home/.evaluationScripts 2>/dev/null || true
chmod 755 /home/.evaluationScripts/activityInitiator 2>/dev/null || true
chmod 666 "$EVAL_DIR/evaluate.json" 2>/dev/null || true

rm -f /tmp/submit_flag.txt
if [ -f "/home/labDirectory/SUBMIT_FLAG.txt" ]; then
  cp /home/labDirectory/SUBMIT_FLAG.txt /tmp/submit_flag.txt
fi

python3 "$EVAL_DIR/autograder.py"
cp /tmp/evaluate.json "$EVAL_DIR/evaluate.json" 2>/dev/null || true
