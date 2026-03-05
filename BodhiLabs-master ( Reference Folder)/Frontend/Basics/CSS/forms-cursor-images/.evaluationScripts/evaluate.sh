#! /bin/bash
ptcd=$(pwd)
cd /home/.evaluationScripts/autograder/
python3 script.py
cd "$ptcd"
