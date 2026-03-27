#!/bin/bash
set -euo pipefail

HOST="${1:-evil.attacker.local}"
PATH_REQ="${2:-/admin}"

curl -s "http://127.0.0.1:8081/fetch?host=${HOST}&path=${PATH_REQ}" | python3 -m json.tool
