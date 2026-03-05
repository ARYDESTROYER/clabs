#!/bin/sh
set -e

# Simple helper used by initactivity.sh to start ZAP WebSwing if needed.
# Lab-B primarily runs ZAP via supervisord.

PORT="${1:-30004}"

if command -v netstat >/dev/null 2>&1; then
  if netstat -tuln | grep -q ":${PORT}\\b"; then
    echo "ZAP WebSwing already listening on port ${PORT}"
    exit 0
  fi
fi

echo "Starting ZAP WebSwing..."
exec sh /zap/zap-webswing.sh

