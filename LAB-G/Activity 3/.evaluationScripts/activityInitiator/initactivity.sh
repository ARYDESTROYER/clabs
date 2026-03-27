#!/bin/bash
# Do not use strict exit-on-error in init scripts.
# This keeps infrastructure setup resilient across LMS variance.

LAB_DIR="/home/labDirectory"
EVAL_DIR="/home/.evaluationScripts"
RUNTIME_DIR="/opt/labg"
ACTIVITY_ID="3"
VICTIM_KEY="labg-victim-key-a3"
INIT_LOG="/tmp/labg_init.log"

if [ -x /usr/lib/jvm/java-17-openjdk-amd64/bin/java ]; then
  JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
  export JAVA_HOME
  export PATH="$JAVA_HOME/bin:$PATH"
elif [ -z "${JAVA_HOME:-}" ] && command -v java >/dev/null 2>&1; then
  JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(command -v java)")")")"
  export JAVA_HOME
fi

chmod 755 "$EVAL_DIR" "$EVAL_DIR/activityInitiator" 2>/dev/null || true
chmod 666 "$EVAL_DIR/evaluate.json" 2>/dev/null || true
mkdir -p "$LAB_DIR" "$RUNTIME_DIR" /zap/wrk /opt
chmod 777 "$LAB_DIR" "$RUNTIME_DIR" /zap/wrk /opt 2>/dev/null || true
chown -R student:student "$LAB_DIR" 2>/dev/null || true

echo "[$(date)] LAB-G init start (Activity ${ACTIVITY_ID})" > "$INIT_LOG"
echo "[$(date)] user=$(id -un 2>/dev/null || whoami)" >> "$INIT_LOG"
echo "[$(date)] python=$(command -v python3 || echo missing)" >> "$INIT_LOG"
echo "[$(date)] supervisord=$(command -v supervisord || echo missing)" >> "$INIT_LOG"
echo "[$(date)] java_home=${JAVA_HOME:-unset}" >> "$INIT_LOG"
java -version >> "$INIT_LOG" 2>&1 || true

touch /opt/labg_app.log /opt/labg_app.err /opt/labg_victim.log /opt/labg_victim.err /opt/labg_zap.log /opt/labg_zap.err 2>/dev/null || true

cp "$EVAL_DIR/activityInitiator/labg_app.py" "$RUNTIME_DIR/labg_app.py"
cp "$EVAL_DIR/activityInitiator/victim_worker.py" "$RUNTIME_DIR/victim_worker.py"
chmod +x "$RUNTIME_DIR/labg_app.py" "$RUNTIME_DIR/victim_worker.py"

if [ -f /zap/webswing/jetty.properties ]; then
  sed -i 's/8080/30004/g' /zap/webswing/jetty.properties
  sed -i 's/org.webswing.server.https=true/org.webswing.server.https=false/g' /zap/webswing/jetty.properties
  sed -i 's/org.webswing.server.host=localhost/org.webswing.server.host=0.0.0.0/g' /zap/webswing/jetty.properties
fi

for f in xss-payload.txt flag.txt; do
  rm -f "$LAB_DIR/$f" 2>/dev/null || true
  : > "$LAB_DIR/$f"
  chown student:student "$LAB_DIR/$f" 2>/dev/null || true
  chmod 777 "$LAB_DIR/$f" 2>/dev/null || true
done

pkill -f labg_app.py 2>/dev/null || true
pkill -f victim_worker.py 2>/dev/null || true
pkill -f zap-webswing.sh 2>/dev/null || true

echo "[$(date)] launching labg_app.py" >> "$INIT_LOG"
ACTIVITY_ID="$ACTIVITY_ID" VICTIM_KEY="$VICTIM_KEY" python3 /opt/labg/labg_app.py >/opt/labg_app.log 2>/opt/labg_app.err &
APP_PID=$!

echo "[$(date)] launching victim_worker.py" >> "$INIT_LOG"
ACTIVITY_ID="$ACTIVITY_ID" VICTIM_KEY="$VICTIM_KEY" python3 /opt/labg/victim_worker.py >/opt/labg_victim.log 2>/opt/labg_victim.err &
VICTIM_PID=$!

if [ -x /zap/zap-webswing.sh ]; then
  echo "[$(date)] launching zap-webswing.sh" >> "$INIT_LOG"
  ZAP_WEBSWING_OPTS="-host 0.0.0.0 -port 30003" /zap/zap-webswing.sh >/opt/labg_zap.log 2>/opt/labg_zap.err &
  ZAP_PID=$!
else
  echo "[$(date)] ERROR: /zap/zap-webswing.sh not executable" >> "$INIT_LOG"
  ZAP_PID=0
fi

sleep 4
echo "[$(date)] pids app=$APP_PID victim=$VICTIM_PID zap=$ZAP_PID" >> "$INIT_LOG"
netstat -tuln 2>/dev/null | grep -E '30000|30004|30003|8080|8090' >> "$INIT_LOG" || true

exit 0
