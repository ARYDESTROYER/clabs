#!/bin/bash

# Arguments for the start, end range and filename to be copied
start=$1
end=$2
filename=$3

# Loop through the specified range of Lab folders
for ((i=start; i<=end; i++)); do
    replica="../Lab$i/.bodhiFiles/$filename"
    rsync -u "$filename" "$replica"
done