#!/bin/bash
# Purpose: Evaluate student submission by running the autograder

# Define paths
EVAL_DIR="/home/.evaluationScripts"
SUBMISSION_FILE_PLURAL="/home/labDirectory/SUBMIT_FLAGS_HERE.txt"
SUBMISSION_FILE_SINGULAR="/home/labDirectory/SUBMIT_FLAG_HERE.txt"
TEMP_SUBMISSION="/tmp/student_flags.txt"
TEMP_OUTPUT="/tmp/evaluate.json"

# Verify environment
if [ ! -d "$EVAL_DIR" ]; then
    echo "Error: Evaluation scripts not found."
    exit 1
fi

# Clean up temp files
[ -f "$TEMP_SUBMISSION" ] && rm "$TEMP_SUBMISSION"
[ -f "$TEMP_OUTPUT" ] && rm "$TEMP_OUTPUT"

# Pick whichever submission file the student actually edited.
SELECTED_SUBMISSION=""
BEST_SCORE=-1
BEST_MTIME=-1

for candidate in "$SUBMISSION_FILE_PLURAL" "$SUBMISSION_FILE_SINGULAR"; do
    if [ ! -f "$candidate" ]; then
        continue
    fi

    VALUE_COUNT=$(awk -F: '
        /^Fragment [1-6]/ || /^Final Decoded Flag/ {
            value=$0
            sub(/^[^:]*:[[:space:]]*/, "", value)
            if (length(value) > 0) count++
        }
        END { print count+0 }
    ' "$candidate")

    MTIME=$(stat -c %Y "$candidate" 2>/dev/null || stat -f %m "$candidate" 2>/dev/null || echo 0)

    if [ "$VALUE_COUNT" -gt "$BEST_SCORE" ] || { [ "$VALUE_COUNT" -eq "$BEST_SCORE" ] && [ "$MTIME" -gt "$BEST_MTIME" ]; }; then
        BEST_SCORE="$VALUE_COUNT"
        BEST_MTIME="$MTIME"
        SELECTED_SUBMISSION="$candidate"
    fi
done

# Copy student's submission to temp (Avoids permission issues in EVAL_DIR)
if [ -n "$SELECTED_SUBMISSION" ]; then
    cp "$SELECTED_SUBMISSION" "$TEMP_SUBMISSION"
else
    echo "Warning: No submission file found (checked SUBMIT_FLAGS_HERE.txt and SUBMIT_FLAG_HERE.txt)." >&2
fi

# Run the Python autograder (it reads from TEMP_SUBMISSION)
python3 "$EVAL_DIR/autograder.py"

# Copy the autograder output back to the mounted directory for the LMS.
cp "$TEMP_OUTPUT" "$EVAL_DIR/evaluate.json" 2>/dev/null || true
