#!/bin/sh
# Evaluation script for Lab-B
set -e

echo "Starting Lab-B evaluation..."

cd /home/.evaluationScripts/autograder
python3 autograder.py

echo ""
echo "Evaluation Results:"
cat /home/.evaluationScripts/evaluate.json

exit 0
