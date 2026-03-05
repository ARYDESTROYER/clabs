#!/bin/bash
# Reset Lab-G to initial state
# Single-container reset: clears runtime artifacts so initactivity.sh re-initializes.

set -e

echo "Resetting Lab-G environment..."

# Clear generated flags (clab standard: /opt/masterflag*.txt)
rm -f /opt/masterflag*.txt

# Force re-initialization on next start
rm -f /opt/secret.txt

# Clear runtime DB and logs
rm -f /app/data/ecommerce.db /app/data/ecommerce.db-journal
rm -f /opt/stdout-*.log /opt/stderr-*.log

# Preserve student submissions, but clear derived artifacts
rm -f /home/labDirectory/exfiltrated-flag.txt
rm -f /home/labDirectory/flag2.txt
rm -f /home/labDirectory/zap-report.html

# Clear evaluation results
rm -f /home/.evaluationScripts/evaluate.json

echo "Lab-G reset complete."
