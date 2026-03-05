#!/bin/bash

cp /home/labDirectory/CartIcon.js /home/.evaluationScripts/src/components/
cp /home/labDirectory/ProductCard.js /home/.evaluationScripts/src/components/
cp /home/labDirectory/Reset.js /home/.evaluationScripts/src/components/
cp /home/labDirectory/index.js /home/.evaluationScripts/src/
cp /home/labDirectory/store.js /home/.evaluationScripts/src/

cd /home/.evaluationScripts

npm test > /dev/null 2>&1

python3 .bodhiFiles/autograder.py
rm .bodhiFiles/out.txt
