#!/bin/sh
set -e

LAB_DIR="/home/labDirectory"
FLAGS_DIR="/opt"
SECRET_FLAG="/home/.evaluationScripts/.initialized"

# Ensure JAVA_HOME is set for /zap/zap-webswing.sh on every container start.
if [ -z "${JAVA_HOME:-}" ] && command -v java >/dev/null 2>&1; then
    JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(command -v java)")")")"
    export JAVA_HOME
fi

if [ -f "$SECRET_FLAG" ]; then
    echo "No Need!"
else
    mkdir -p "$FLAGS_DIR" "$LAB_DIR"
    chmod 777 "$FLAGS_DIR"
    chmod 777 "$LAB_DIR"

    # Configure ZAP ports (WebSwing GUI + API). Proxy remains on 8080.
    # Disable HTTPS to avoid port conflicts and simplify setup.
    if [ -f /zap/webswing/jetty.properties ]; then
        sed -i 's/8080/30004/g' /zap/webswing/jetty.properties
        sed -i 's/org.webswing.server.https=true/org.webswing.server.https=false/g' /zap/webswing/jetty.properties
        sed -i 's/org.webswing.server.host=localhost/org.webswing.server.host=0.0.0.0/g' /zap/webswing/jetty.properties
    fi
    if [ -f /zap/webswing/webswing.config ]; then
        sed -i 's/8090/30003/g' /zap/webswing/webswing.config
    fi
    if [ -f /zap/zap-webswing.sh ]; then
        sed -i 's/8090/30003/g' /zap/zap-webswing.sh
    fi

    # Copy helper script (optional) into the ZAP directory.
    if [ -f /home/.evaluationScripts/activityInitiator/zaprunner.sh ]; then
        cp /home/.evaluationScripts/activityInitiator/zaprunner.sh /zap/
        chmod +x /zap/zaprunner.sh || true
    fi

    mkdir -p /zap/wrk || true
    chmod 777 /zap/wrk || true

    cp /home/.evaluationScripts/activityInitiator/config/supervisord.conf /etc/supervisord.conf

    cat > "$LAB_DIR/README.txt" << 'DOC'
Lab-B: Network Recon & Device Efficacy Audit
===========================================

Objective:
- Assess WAF/firewall effectiveness
- Discover hidden admin console
- Use header tampering to bypass controls

Target:
- http://localhost:30000

Services:
- OWASP ZAP GUI: http://localhost:30004 (browser-based)
- ZAP API: http://localhost:30003
- ZAP Proxy: http://localhost:8080

How to capture flags:
- FLAG1: send a successful `/rest/products/search` request that contains a `UNION SELECT`-style payload and copy the `X-Lab-Flag1` response header.
- FLAG2: access `/internal/device-status` and copy the JSON field `flag` (requires `X-Forwarded-For: 10.0.0.1`).
- FLAG3: reach `/admin-console` via the misapplied `X-Original-URL` routing header and copy the `FLAG3:` value in the HTML.
- FLAG4: reach `/rest/admin/application-version` via the same routing issue and copy the JSON field `flag`.

Submission Files:
- discovery.txt
- enumeration.txt
- bypass-technique.txt
- flag.txt

DOC

    chmod 644 "$LAB_DIR/README.txt"

    # Create expected submission files for students/platform.
    for file in discovery.txt enumeration.txt bypass-technique.txt flag.txt; do
        if [ ! -f "$LAB_DIR/$file" ]; then
            : > "$LAB_DIR/$file"
        fi
        chmod 666 "$LAB_DIR/$file" || true
    done
    echo Done > "$SECRET_FLAG"
fi

exec /usr/bin/supervisord -c /etc/supervisord.conf
