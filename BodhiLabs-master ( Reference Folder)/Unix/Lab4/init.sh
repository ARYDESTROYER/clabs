#!/bin/bash
if [ -f "/opt/check.txt" ]; then
    echo "No Need!"
else
    cp -r /home/.evaluationScripts/.bodhiFiles/studentDirectory/* /home/labDirectory/
    chmod ugo+r /home/labDirectory/*
    chmod ugo+w /home/labDirectory/answer.txt
    echo Done > /opt/check.txt
fi

# Set up the environment
sh /home/.evaluationScripts/init_helper.sh

# Start the bash shell
exec /bin/bash
