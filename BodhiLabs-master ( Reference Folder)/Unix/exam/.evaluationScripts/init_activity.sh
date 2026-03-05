#!/bin/bash
if [ -f "/opt/check.txt" ]; then
    echo "No Need!"
else
    for i in {1..4}; do
        touch /home/labDirectory/part-$i/answer-$i.txt
        chmod +w /home/labDirectory/part-$i/answer-$i.txt
    done
    echo Done > /opt/check.txt
fi

# Start the bash shell
exec /bin/bash
