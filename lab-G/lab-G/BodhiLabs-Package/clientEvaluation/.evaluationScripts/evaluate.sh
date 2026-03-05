#!/bin/bash
# Evaluation script for Lab-G
# Entry point called by the platform

set -e

echo "Starting Lab-G evaluation..."

# Change to autograder directory
cd /home/.evaluationScripts/autograder

# Run autograder
python3 autograder.py

# Display results
echo ""
echo "Evaluation Results:"
cat /home/.evaluationScripts/evaluate.json

# Return success
exit 0
