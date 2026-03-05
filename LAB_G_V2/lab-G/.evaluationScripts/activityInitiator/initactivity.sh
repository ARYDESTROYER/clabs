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

    # Disable HTTPS connector (port 8443) to prevent crash-loop
    sed -i 's/org.webswing.server.https=true/org.webswing.server.https=false/' /zap/webswing/jetty.properties
    sed -i 's/org.webswing.server.https.port=8443/org.webswing.server.https.port=0/' /zap/webswing/jetty.properties

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
Lab-G: Stored XSS Tutorial (TechStore)
======================================

OBJECTIVE:
Learn Stored XSS through 4 guided activities:
1) Basic reconnaissance and XSS fundamentals
2) Automated recon with OWASP ZAP
3) Pop first XSS payload
4) Escalate to admin and capture FLAG4 via CLI listener

SERVICES:
- Ecommerce App: http://localhost:30000
- OWASP ZAP GUI: http://localhost:30004 (WebSwing - browser-based)
- ZAP Proxy: localhost:8080 (optional)

ADMIN CREDENTIALS:
- Username: admin
- Password: SecureAdminPass2025!

FLAGS:
- Only FLAG1 and FLAG4 are required for grading.

See handout-lab-G.md for step-by-step activity instructions.

Good luck!
EOF

    chmod 644 /home/labDirectory/README.txt

    # Pre-create evaluate.json with correct permissions (REQUIRED by BodhiLabs)
    touch /home/.evaluationScripts/evaluate.json
    chmod 666 /home/.evaluationScripts/evaluate.json

    # Pre-create writable submission files for students
    touch /home/labDirectory/flag.txt
    touch /home/labDirectory/xss-payload.txt
    chmod 666 /home/labDirectory/flag.txt /home/labDirectory/xss-payload.txt

    # Mark as initialized
    echo Done > /opt/secret.txt

    echo "Lab-G initialized successfully!"
fi

# Start supervisord (manages Flask app, ZAP, and Victim bot)
echo "Starting all services..."
/usr/bin/supervisord -c /etc/supervisord.conf
