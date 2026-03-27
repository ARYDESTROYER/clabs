#!/bin/bash
set -euo pipefail

LAB_DIR="/home/labDirectory"
EVAL_DIR="/home/.evaluationScripts"

chmod 666 "$EVAL_DIR/evaluate.json" 2>/dev/null || true
touch "$LAB_DIR/SUBMIT_FLAG.txt"
echo "(Paste only the Activity 1 flag)" > "$LAB_DIR/SUBMIT_FLAG.txt"
chmod 666 "$LAB_DIR/SUBMIT_FLAG.txt"

cp "$EVAL_DIR/activityInitiator/runtime_stack.py" /usr/local/bin/runtime_stack.py
cp "$EVAL_DIR/activityInitiator/labfctl.sh" /usr/local/bin/labfctl
cp "$EVAL_DIR/activityInitiator/rebindctl.sh" /usr/local/bin/rebindctl
cp "$EVAL_DIR/activityInitiator/fetch_sim.sh" /usr/local/bin/fetch-sim
chmod +x /usr/local/bin/runtime_stack.py /usr/local/bin/labfctl /usr/local/bin/rebindctl /usr/local/bin/fetch-sim

LABF_ACTIVITY=1 /usr/local/bin/runtime_stack.py stop || true
LABF_ACTIVITY=1 /usr/local/bin/runtime_stack.py reset
LABF_ACTIVITY=1 /usr/local/bin/runtime_stack.py start

cat > "$LAB_DIR/SCENARIO.txt" << 'EOF'
Activity 1 (Guided): Manual Rebinding Pivot

1) Open browser UI: http://127.0.0.1:8080
2) Confirm baseline state:
    labfctl status
3) Probe admin before pivot (expected 404):
    fetch-sim evil.attacker.local /admin
4) Manually rebind host to internal admin-a:
    labfctl set evil.attacker.local admin-a
5) Probe admin again (expected 200 with token):
    fetch-sim evil.attacker.local /admin
6) Put the IITB{...} token into SUBMIT_FLAG.txt

Extra observability:
- Proxy route log: labfctl logs proxy
- Exfil log:       labfctl logs exfil
EOF

echo "[+] Activity 1 initialized. Browser console: http://127.0.0.1:8080"
