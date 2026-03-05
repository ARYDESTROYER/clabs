#!/bin/bash
# Purpose: Evaluate student submission by running the autograder

# Define paths
EVAL_DIR="/home/.evaluationScripts"
SUBMISSION_FILE="SUBMIT_FLAG_HERE.txt"
STUDENT_SUBMISSION="/home/labDirectory/$SUBMISSION_FILE"
TEMP_SUBMISSION="/tmp/student_flag.txt"

# Verify environment
if [ ! -d "$EVAL_DIR" ]; then
    echo "Error: Evaluation scripts not found."
    exit 1
fi

# Clean up temp file
[ -f "$TEMP_SUBMISSION" ] && rm "$TEMP_SUBMISSION"

# Copy student's submission to temp (Avoids permission issues in EVAL_DIR)
if [ -f "$STUDENT_SUBMISSION" ]; then
    cp "$STUDENT_SUBMISSION" "$TEMP_SUBMISSION"
    # Ensure readable
    chmod 644 "$TEMP_SUBMISSION"
else
    echo "Warning: SUBMIT_FLAG_HERE.txt not found in student directory." >&2
fi

# Run the Python autograder (it reads from TEMP_SUBMISSION)
python3 "$EVAL_DIR/autograder.py"
