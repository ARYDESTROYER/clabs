#!/bin/sh
# Reset Lab-B environment
set -e

FLAGS_DIR="/opt"

if [ -d "$FLAGS_DIR" ]; then
    rm -f "$FLAGS_DIR"/masterflag*.txt
fi

if [ -d "/usr/local/apache2/logs" ]; then
    : > "/usr/local/apache2/logs/access_log" 2>/dev/null || true
    : > "/usr/local/apache2/logs/error_log" 2>/dev/null || true
fi

echo "Lab-B reset complete."
