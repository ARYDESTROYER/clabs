#!/bin/bash

cd /home/.evaluationScripts/.bodhiFiles
[ -f answer.txt ] && rm answer.txt
cp /home/labDirectory/answer.txt /home/.evaluationScripts/.bodhiFiles/
# Delete everything in /home/labDirectory except answer.txt
for item in /home/labDirectory/*; do
    [ "$(basename "$item")" != "answer.txt" ] && rm -rf "$item"
done
cp -r /home/.evaluationScripts/.bodhiFiles/studentDirectory/* /home/labDirectory/
python3 /home/.evaluationScripts/.bodhiFiles/autograder.py
