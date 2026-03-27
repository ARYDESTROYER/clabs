#!/bin/bash
set -euo pipefail

CTL_URL="http://127.0.0.1:8085"

usage() {
  cat <<'EOF'
Usage:
  labfctl status
  labfctl reset
  labfctl set <host> <attacker|admin-a|admin-b>
  labfctl arm [threshold]
  labfctl logs <proxy|exfil>
  labfctl clear-logs
  labfctl open
EOF
}

cmd="${1:-}"
case "$cmd" in
  status)
    curl -s "$CTL_URL/status" | python3 -m json.tool
    ;;
  reset)
    curl -s "$CTL_URL/reset" | python3 -m json.tool
    ;;
  set)
    host="${2:-evil.attacker.local}"
    target="${3:-attacker}"
    curl -s "$CTL_URL/set?host=$host&target=$target" | python3 -m json.tool
    ;;
  arm)
    threshold="${2:-3}"
    curl -s "$CTL_URL/arm?threshold=$threshold" | python3 -m json.tool
    ;;
  logs)
    type="${2:-proxy}"
    if [[ "$type" == "proxy" ]]; then
      curl -s "http://127.0.0.1:8083/logs"
    elif [[ "$type" == "exfil" ]]; then
      curl -s "http://127.0.0.1:8084/logs"
    else
      echo "Invalid log type: $type" >&2
      exit 1
    fi
    ;;
  clear-logs)
    curl -s "$CTL_URL/clear-logs" | python3 -m json.tool
    ;;
  open)
    echo "Open in browser: http://127.0.0.1:8080"
    ;;
  *)
    usage
    exit 1
    ;;
esac
