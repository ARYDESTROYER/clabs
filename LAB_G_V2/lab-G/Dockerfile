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
    net-tools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy application code and evaluation scripts
COPY .evaluationScripts/activityInitiator/python-app/ /app/
COPY .evaluationScripts/ /home/.evaluationScripts/
COPY handout-lab-G.md /home/labDirectory/handout-lab-G.md

# Install Python dependencies
RUN pip3 install --no-cache-dir --break-system-packages -r /app/requirements.txt

# Install Selenium for victim bot
RUN pip3 install --no-cache-dir --break-system-packages selenium

# Create necessary directories
RUN mkdir -p /app/data /home/labDirectory /opt /var/log

# Set permissions
RUN chmod +x /home/.evaluationScripts/activityInitiator/*.sh \
    && chmod +x /home/.evaluationScripts/evaluate.sh \
    && chmod 777 /home/labDirectory \
    && chmod 777 /opt \
    && chmod 777 /var/log

# Expose ports
# 30000: Flask application
# 30003: ZAP API
# 30004: ZAP WebSwing GUI
# 8080: ZAP Proxy
EXPOSE 30000 30003 30004 8080

# Run initactivity.sh on container start
CMD ["/bin/bash", "/home/.evaluationScripts/activityInitiator/initactivity.sh"]
