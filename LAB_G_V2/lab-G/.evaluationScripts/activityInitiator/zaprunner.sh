#!/bin/bash

# Define the TCP port to check (WebSwing GUI port, remapped from 8080)
PORT=30004

# Check if the port is open using netstat
netstat -tuln | grep -q ":$PORT\b"

# Check the exit status of grep
if [ $? -ne 0 ]; then
    # If the port is not open, run zap-webswing.sh
    echo "Port $PORT is not open. Running zap-webswing.sh..."
    bash /zap/zap-webswing.sh
else
    echo "Port $PORT is open. ZAP WebSwing is running."
fi
