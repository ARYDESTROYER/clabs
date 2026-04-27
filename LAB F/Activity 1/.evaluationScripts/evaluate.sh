#!/bin/bash
# LAB F Activity 1 -- /tmp write pattern (Section 7.7 of BODHILABS guide).

EVAL_DIR="/home/.evaluationScripts"
SUBMISSION="$EVAL_DIR/.." # unused, kept for clarity

chmod 755 "$EVAL_DIR" 2>/dev/null || true
chmod 755 "$EVAL_DIR/activityInitiator" 2>/dev/null || true
chmod 666 "$EVAL_DIR/evaluate.json" 2>/dev/null || true

for f in flag.txt; do
    rm -f "/tmp/$f"
    if [ -f "/home/labDirectory/$f" ]; then
        cp "/home/labDirectory/$f" "/tmp/$f"
        chmod 644 "/tmp/$f"
    fi
done

python3 "$EVAL_DIR/autograder.py"

# Best-effort copy back to the mount; if it fails the LMS still gets the file
# from /tmp via its evaluate.sh hook in many configurations.
cp /tmp/evaluate.json "$EVAL_DIR/evaluate.json" 2>/dev/null || true
