#!/bin/bash
# clears runtime artifacts so initactivity.sh re-initializes.

set -e

echo "Resetting Lab-G environment..."

rm -f /opt/masterflag*.txt

rm -f /opt/secret.txt

rm -f /app/data/ecommerce.db /app/data/ecommerce.db-journal
rm -f /opt/stdout-*.log /opt/stderr-*.log

rm -f /home/labDirectory/exfiltrated-flag.txt

rm -f /home/.evaluationScripts/evaluate.json

echo "Lab-G reset complete."
