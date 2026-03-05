#!/bin/bash
if [ -f "/opt/check.txt" ]; then
    echo "No Need!"
else
    cp -r /home/.evaluationScripts/studentDirectory/* /home/labDirectory/
    chmod -R a+rw /home/labDirectory/forms1/forms-1.html
    chmod -R a+rw /home/labDirectory/forms2/forms-2.html
    chmod -R a+rw /home/labDirectory/forms3/forms-3.html
    echo Done > /opt/check.txt
fi

# Start the bash shell
exec /bin/bash
