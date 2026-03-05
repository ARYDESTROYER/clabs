#!/bin/bash

cd /home/.evaluationScripts/.bodhiFiles
[ -f answer.txt ] && rm answer.txt
cp /home/labDirectory/answer.txt /home/.evaluationScripts/.bodhiFiles/
python3 /home/.evaluationScripts/.bodhiFiles/autograder.py
