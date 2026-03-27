#!/bin/bash
set -euo pipefail

rm -f /tmp/labg_state.json
pkill -f labg_app.py 2>/dev/null || true
pkill -f victim_worker.py 2>/dev/null || true

/usr/bin/supervisord -c /etc/supervisord.conf
