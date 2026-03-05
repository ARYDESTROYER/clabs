#!/bin/bash
# Initialize Lab-G in single container
# Runs INSIDE the OWASP ZAP container

if [ -f "/opt/secret.txt" ]
then
    echo "Lab already initialized!"
else
    echo "Initializing Lab-G: Stored XSS Challenge..."

    # Configure ZAP ports (WebSwing)
    sed -i 's/8080/30004/g' /zap/webswing/jetty.properties
    sed -i 's/8090/30003/g' /zap/webswing/webswing.config
    sed -i 's/8090/30003/g' /zap/zap-webswing.sh

    # Copy ZAP runner script
    cp /home/.evaluationScripts/activityInitiator/zaprunner.sh /zap/
    chmod +x /zap/zaprunner.sh

    # Copy supervisord config
    cp /home/.evaluationScripts/activityInitiator/config/supervisord.conf /etc/supervisord.conf

    # Initialize Flask app database
    mkdir -p /app/data
    cd /app
    python3 init_db.py

    # Create directories
    mkdir -p /home/labDirectory
    
    chmod 777 /home/labDirectory
    

    # Create README for students
    cat > /home/labDirectory/README.txt << 'EOF'
Lab-G: Stored XSS & OWASP ZAP Challenge
========================================

OBJECTIVE:
Find and exploit XSS vulnerabilities in the TechStore ecommerce application.

SERVICES:
- Ecommerce App: http://localhost:30000
- OWASP ZAP GUI: http://localhost:30004 (WebSwing - browser-based)
- ZAP Proxy: localhost:8080 (configure in your browser)
- Exploit Dashboard: http://localhost:30000/dashboard

ADMIN CREDENTIALS:
- Username: admin
- Password: SecureAdminPass2024!

CHALLENGE: Find and exploit XSS vulnerabilities to capture 4 flags.
Check README.txt in /home/labDirectory for full instructions.

Good luck!
EOF

    chmod 644 /home/labDirectory/README.txt

    # Mark as initialized
    echo Done > /opt/secret.txt

    echo "Lab-G initialized successfully!"
fi

# Start supervisord (manages Flask app, ZAP, and Victim bot)
echo "Starting all services..."
/usr/bin/supervisord -c /etc/supervisord.conf
