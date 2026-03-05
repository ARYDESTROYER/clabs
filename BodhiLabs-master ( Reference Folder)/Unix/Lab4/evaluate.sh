#!/bin/bash

cd /home/.evaluationScripts/.bodhiFiles
[ -f answer.txt ] && rm answer.txt
[ -f /home/labDirectory/output.txt ] && rm /home/labDirectory/output.txt
cp /home/labDirectory/answer.txt /home/.evaluationScripts/.bodhiFiles/
python3 /home/.evaluationScripts/.bodhiFiles/autograder.py
