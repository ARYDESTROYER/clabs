#! /bin/bash

cd /home/.evaluationScripts/
[ -f tables.html ] && rm tables.html
cp /home/labDirectory/tables.html /home/.evaluationScripts/
python3 /home/.evaluationScripts/autograder.py
