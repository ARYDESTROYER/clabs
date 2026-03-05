#!/bin/bash

# Check if exactly one argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <Lab Name>"
    exit 1
fi

lab=$1

studentFile="$lab/.bodhiFiles/studentFiles"

rsync -a --exclude="node_modules" "$lab/" ".evaluationScripts/"
tar -czvf instructor.tgz .evaluationScripts

rsync -a --exclude="node_modules" "$studentFile/" "labDirectory/"
tar -czvf student.tgz labDirectory

# Remove the copied and renamed folders
rm -rf .evaluationScripts labDirectory
