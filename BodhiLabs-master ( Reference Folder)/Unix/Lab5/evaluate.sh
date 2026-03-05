#!/bin/bash

cd /home/.evaluationScripts/.bodhiFiles
# Remove old answer.txt if present
[ -f answer.txt ] && rm answer.txt
# Copy latest student answer
cp /home/labDirectory/answer.txt /home/.evaluationScripts/.bodhiFiles/
# Cleanup: remove everything in /home/labDirectory except answer.txt and file4.txt
find /home/labDirectory/ -mindepth 1 ! -name 'answer.txt' ! -name 'file4.txt' -exec rm -rf {} +
# Run autograder
sudo python3 /home/.evaluationScripts/.bodhiFiles/autograder.py
