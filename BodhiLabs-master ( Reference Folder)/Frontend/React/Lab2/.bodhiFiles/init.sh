#!/bin/bash
if [ -f "/opt/headerfooterlist.txt" ]; then
    echo "No Need!"
else
    cp /home/.evaluationScripts/.bodhiFiles/studentFiles/* /home/labDirectory/
    chmod 777 /home/labDirectory/*
    echo Done > /opt/headerfooterlist.txt
fi

cd /home/.evaluationScripts
npm install
PORT=30000 npm start