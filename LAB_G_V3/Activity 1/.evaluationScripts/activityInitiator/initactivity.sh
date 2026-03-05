#!/bin/sh
# set -e

# --- Part 1: Infrastructure Setup ---
# Pre-create evaluate.json to avoid permission errors
sudo touch /home/.evaluationScripts/evaluate.json
sudo chmod 666 /home/.evaluationScripts/evaluate.json

# Ensure scripts are executable (mounted files might lose +x)
chmod +x /home/.evaluationScripts/evaluate.sh
chmod +x /home/.evaluationScripts/activityInitiator/initactivity.sh

LAB_DIR="/home/labDirectory"
INIT_MARKER="/opt/lab-z-initialized"

if [ -z "${JAVA_HOME:-}" ] && command -v java >/dev/null 2>&1; then
    JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(command -v java)")")")"
    export JAVA_HOME
fi

if [ ! -f "$INIT_MARKER" ]; then
    echo "Initializing Lab-Z: Juice Shop + ZAP..."

    # Set ZAP WebSwing host/port so UI is reachable on 30004.
    if [ -f /zap/webswing/jetty.properties ]; then
        sed -i 's/^org.webswing.server.host=.*/org.webswing.server.host=0.0.0.0/' /zap/webswing/jetty.properties
        sed -i 's/^org.webswing.server.http.port=.*/org.webswing.server.http.port=30004/' /zap/webswing/jetty.properties
        sed -i 's/^org.webswing.server.https=.*/org.webswing.server.https=false/' /zap/webswing/jetty.properties
    fi

    cp /home/.evaluationScripts/activityInitiator/config/supervisord.conf /etc/supervisord.conf

    mkdir -p "$LAB_DIR"
    cat > "$LAB_DIR/README.txt" <<'DOC'
Lab-Z: OWASP ZAP Fundamentals with Juice Shop
============================================

Target App:
- http://localhost:30000

OWASP ZAP:
- GUI (WebSwing): http://localhost:30004/zap/

Single Activity Goal:
- Learn ZAP setup and core interface
- Run spider and active scan
- Discover requests from app traffic and practice fuzzing
DOC

    chmod 644 "$LAB_DIR/README.txt"
    echo "initialized" > "$INIT_MARKER"
fi

exec /usr/bin/supervisord -c /etc/supervisord.conf
