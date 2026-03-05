# Lab-G: Stored XSS Challenge

FROM zaproxy/zap-stable:latest

USER root

# Install required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    supervisor \
    sqlite3 \
    curl \
    wget \
    chromium \
    chromium-driver \
    cron \
    netstat-nat \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Scripts and App code come from tarball mount at /home/.evaluationScripts
# No COPY commands here.

# Install Python dependencies (Hardcoded since requirements.txt isn't available at build)
RUN pip3 install --no-cache-dir --break-system-packages Flask==3.0.0 Werkzeug==3.0.1 Jinja2==3.1.2 selenium

# Create necessary directories
RUN mkdir -p /app/data /home/labDirectory /opt /var/log

# Permissions managed in initactivity.sh
# Port 30003: ZAP API, 30004: ZAP GUI, 8080: Proxy
EXPOSE 30000 30003 30004 8080

# Run initactivity.sh on container start (keeps container alive)
CMD ["/bin/bash", "-c", "bash /home/.evaluationScripts/activityInitiator/initactivity.sh; while :; do sleep 10; done"]
