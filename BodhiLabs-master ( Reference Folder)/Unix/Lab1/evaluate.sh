#!/bin/bash

cd /home/.evaluationScripts/.bodhiFiles
[ -f answer.txt ] && rm answer.txt
cp /home/labDirectory/command.txt /home/.evaluationScripts/.bodhiFiles/
cp /home/labDirectory/filename.txt /home/.evaluationScripts/.bodhiFiles/
python3 /home/.evaluationScripts/.bodhiFiles/autograder.py
